from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.note import Note

note_bp = Blueprint('note', __name__)

@note_bp.route('/', methods=['POST'])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    note = Note(
        user_id=user_id,
        course_id=data.get('course_id'),
        title=data.get('title'),
        content=data.get('content')
    )
    db.session.add(note)
    db.session.commit()
    
    return jsonify({"message": "Note created", "id": note.id}), 201

@note_bp.route('/', methods=['GET'])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())
    course_id = request.args.get('course_id')
    
    query = Note.query.filter_by(user_id=user_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
        
    notes = query.order_by(Note.last_edited.desc()).all()
    
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "content": n.content,
        "course_id": n.course_id,
        "last_edited": n.last_edited
    } for n in notes]), 200

@note_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
        
    if 'title' in data: note.title = data['title']
    if 'content' in data: note.content = data['content']
    
    db.session.commit()
    return jsonify({"message": "Note updated"}), 200

@note_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
        
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"}), 200
