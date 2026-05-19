import contextlib
import os
import tempfile

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db, limiter
from app.models.timetable_entry import TimetableEntry
from app.models.user import User
from app.services.timetable_service import (
    parse_timetable,
    ensure_timetable_flag,
    has_schedule_blocks,
    user_has_timetable,
)

timetable_bp = Blueprint('timetable', __name__)


@timetable_bp.route('/upload', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_timetable():
    user_id = int(get_jwt_identity())

    if 'timetable' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['timetable']

    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.lower().endswith('.xlsx'):
        return jsonify({
            "error": "Invalid file type",
            "message": "Please upload an Excel file (.xlsx)"
        }), 400

    with tempfile.NamedTemporaryFile(
        suffix='.xlsx', delete=False
    ) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = parse_timetable(tmp_path, user_id)
    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)

    if not result['success']:
        return jsonify({
            "error": result['error']
        }), 422

    return jsonify({
        "message": "Timetable uploaded successfully",
        "entries_saved": result['entries_saved'],
        "classes_detected": result['classes'],
        "skipped": result['skipped']
    }), 200


@timetable_bp.route('/my-classes', methods=['GET'])
@jwt_required()
def get_my_classes():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    entries = TimetableEntry.query.filter_by(
        user_id=user_id
    ).order_by(
        TimetableEntry.day_of_week,
        TimetableEntry.start_time
    ).all()

    day_order = {
        'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
        'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7
    }

    return jsonify({
        "classes": [
            {
                "id": e.id,
                "course_code": e.course_code,
                "course_name": e.course_name,
                "day": e.day_of_week,
                "start_time": e.start_time.strftime('%H:%M'),
                "end_time": e.end_time.strftime('%H:%M'),
                "venue": e.venue,
                "section": e.section
            }
            for e in sorted(
                entries,
                key=lambda x: (
                    day_order.get(x.day_of_week, 9),
                    x.start_time
                )
            )
        ],
        "timetable_uploaded": ensure_timetable_flag(user_id) if user else False,
        "schedule_generated": has_schedule_blocks(user_id) if user else False,
    })


@timetable_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_timetable():
    user_id = int(get_jwt_identity())
    TimetableEntry.query.filter_by(user_id=user_id).delete()
    user = User.query.get(user_id)
    if user:
        user.timetable_uploaded = False
    db.session.commit()
    return jsonify({"message": "Timetable cleared"}), 200
