from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import SavedResource
from app.models.user import User
from app import db
from sqlalchemy.exc import IntegrityError
import traceback

material_bp = Blueprint('material', __name__)


@material_bp.route('/search', methods=['POST'])
@jwt_required()
def search_materials():
    """Search for learning resources using the Gemini-powered scraper."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip() if data else ''

        if not query:
            return jsonify({"results": [], "warning": "Please enter a search topic."}), 200

        print(f"Material search request: '{query}'", flush=True)

        from app.utils.material_scraper import MaterialScraper
        scraper = MaterialScraper()
        results = scraper.fetch_academic_materials(query)

        # Check for under-minimum results
        if len(results) < 1:
            return jsonify({
                "results": results,
                "warning": "Couldn't find enough verified resources for that topic. Try rephrasing your search."
            }), 200

        return jsonify({"results": results}), 200

    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"\n!!! SEARCH CRASH !!!\n{error_traceback}", flush=True)
        return jsonify({
            "results": [],
            "warning": "Search timed out or failed. Please try again."
        }), 200


@material_bp.route('/saved', methods=['GET'])
@jwt_required()
def get_saved_resources():
    """Return all saved resources for the current user."""
    try:
        user_id = int(get_jwt_identity())
        saved = SavedResource.query.filter_by(user_id=user_id)\
            .order_by(SavedResource.saved_at.desc()).all()

        return jsonify([{
            "id": s.id,
            "title": s.title,
            "url": s.url,
            "type": s.resource_type,
            "saved_at": s.saved_at.isoformat()
        } for s in saved]), 200

    except Exception as e:
        print(f"Error fetching saved resources: {e}", flush=True)
        return jsonify({"error": "Failed to load saved resources."}), 500


@material_bp.route('/saved', methods=['POST'])
@jwt_required()
def save_resource():
    """Save a resource to the current user's library."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('title') or not data.get('url'):
            return jsonify({"error": "Title and URL are required."}), 400

        resource = SavedResource(
            user_id=user_id,
            title=data['title'],
            url=data['url'],
            resource_type=data.get('type', 'textbook')
        )
        db.session.add(resource)
        db.session.commit()

        return jsonify({
            "id": resource.id,
            "title": resource.title,
            "url": resource.url,
            "type": resource.resource_type,
            "saved_at": resource.saved_at.isoformat()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "You've already saved this resource."}), 409

    except Exception as e:
        db.session.rollback()
        print(f"Error saving resource: {e}", flush=True)
        return jsonify({"error": "Failed to save resource."}), 500


@material_bp.route('/saved/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_saved_resource(resource_id):
    """Remove a saved resource from the user's library."""
    try:
        user_id = int(get_jwt_identity())
        resource = SavedResource.query.filter_by(
            id=resource_id, user_id=user_id
        ).first()

        if not resource:
            return jsonify({"error": "Resource not found."}), 404

        db.session.delete(resource)
        db.session.commit()
        return jsonify({"message": "Resource removed."}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting resource: {e}", flush=True)
        return jsonify({"error": "Failed to remove resource."}), 500