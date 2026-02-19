from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import Material, Course
from app.models.user import User
import traceback 

material_bp = Blueprint('material', __name__)

@material_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_materials(course_id):
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Safety Check 1: Ensure user actually exists in DB
        if not user:
            return jsonify({"error": "User not found in database"}), 401
            
        # Verify course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
            
        style_pref = user.learning_style or "Visual"
        materials = Material.query.filter_by(course_id=course_id).all()
        
        # If no materials found, fetch from Gemini
        if not materials:
            print(f"No materials found for {course.name}. Fetching from Gemini...")
            
            # If these imports fail, the except block below will catch it!
            from app.utils.material_scraper import MaterialScraper
            from app import db
            
            scraper = MaterialScraper()
            # In material_routes.py
            search_term = f"{course.name} computer science course"
            fetched_resources = scraper.fetch_academic_materials(search_term)
            # fetched_resources = scraper.fetch_academic_materials(course.name)
            
            new_materials = []
            for res in fetched_resources:
                mat_type = res.get('type', 'article').lower() 
                if 'video' in mat_type: mat_type = 'video'
                elif 'text' in mat_type: mat_type = 'textbook'
                
                m = Material(
                    course_id=course.id,
                    title=res.get('title'),
                    url=res.get('url'),
                    material_type=mat_type,
                    learning_style_tag=res.get('learning_style_tag', 'Read/Write'),
                    difficulty_level=3 
                )
                new_materials.append(m)
                db.session.add(m)
            
            if new_materials:
                db.session.commit()
                materials = new_materials

        def sort_key(m):
            style_match = 0 if m.learning_style_tag == style_pref else 1
            return (style_match, m.difficulty_level)
            
        sorted_materials = sorted(materials, key=sort_key)
        
        return jsonify([{
            "id": m.id,
            "title": m.title,
            "url": m.url,
            "type": m.material_type,
            "tag": m.learning_style_tag,
            "difficulty": m.difficulty_level
        } for m in sorted_materials]), 200

    except Exception as e:
        # THE X-RAY: This catches the silent crash and sends it to your frontend
        error_traceback = traceback.format_exc()
        print("\n!!! CRITICAL ROUTE CRASH !!!")
        print(error_traceback)
        return jsonify({
            "error": "Backend crashed while processing materials.",
            "details": str(e),
            "traceback": error_traceback
        }), 500