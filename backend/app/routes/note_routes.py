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
        "created_at": n.created_at,
        "last_edited": n.last_edited,
        "file_path": n.file_path,
        "file_type": n.file_type
    } for n in notes]), 200

@note_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_note_file():
    user_id = int(get_jwt_identity())
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    title = request.form.get('title', 'Untitled Upload')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    allowed_extensions = ('.pdf', '.pptx', '.ppt', '.docx')
    if not file or not file.filename.lower().endswith(allowed_extensions):
        return jsonify({"error": "Invalid file type. Only PDF, PPTX, and DOCX allowed."}), 400

    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    filename = secure_filename(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)
    
    # Convert non-PDF files to PDF using LibreOffice
    if not filename.lower().endswith('.pdf'):
        try:
            from app.utils.file_converter import convert_to_pdf
            pdf_path = convert_to_pdf(save_path, upload_folder)
            # Delete the original file after successful conversion
            os.remove(save_path)
            filename = os.path.basename(pdf_path)
            print(f"Converted to PDF: {filename}", flush=True)
        except Exception as e:
            # Clean up the uploaded file on failure
            if os.path.exists(save_path):
                os.remove(save_path)
            print(f"LibreOffice conversion failed: {e}", flush=True)
            return jsonify({
                "error": "File conversion failed. Make sure LibreOffice is installed."
            }), 500
    
    note = Note(
        user_id=user_id,
        title=title,
        content=f"File upload: {filename}",
        file_path=filename,
        file_type='pdf'  # Always PDF after conversion
    )
    db.session.add(note)
    db.session.commit()
    
    return jsonify({"message": "File uploaded", "id": note.id, "file_url": filename}), 201

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

# @note_bp.route('/file/<filename>', methods=['GET'])
# def serve_note_file(filename):
#     from flask import send_from_directory, current_app, abort
#     import os
    
#     upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
#     try:
#         return send_from_directory(upload_folder, filename)
#     except FileNotFoundError:
#         abort(404)

@note_bp.route('/file/<filename>', methods=['GET'])
def serve_note_file(filename):
    from flask import send_from_directory, current_app, abort, make_response
    import os
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        response = make_response(send_from_directory(upload_folder, filename, as_attachment=False))
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline'
        return response
    except FileNotFoundError:
        abort(404)

