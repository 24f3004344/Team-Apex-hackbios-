"""
Hospital routes for accessing government hospital data.
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from models import hospital as hospital_model
from middleware.auth_middleware import login_required

hospitals_bp = Blueprint('hospitals', __name__, url_prefix='/hospitals')


# Make helper available in templates
@hospitals_bp.app_template_global()
def get_nearby_hospitals_global(district, exclude_id, limit=5):
    """Template global for getting nearby hospitals."""
    return hospital_model.nearby(district, exclude_id, limit)


@hospitals_bp.route('/')
@login_required
def list_hospitals():
    """List all hospitals with pagination and filtering."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    district = request.args.get('district', '')
    hospital_type = request.args.get('type', '')
    search = request.args.get('search', '')

    total = hospital_model.count(district, hospital_type, search)
    hospitals_list = hospital_model.list_paginated(district, hospital_type, search, per_page, (page - 1) * per_page)

    # Fetch up to 150 matching hospitals with coordinates for interactive map rendering
    map_hospitals = hospital_model.list_for_map(district, hospital_type, search)

    return render_template('hospitals/list.html',
                           hospitals=hospitals_list,
                           map_hospitals=map_hospitals,
                           districts=hospital_model.districts(),
                           types=hospital_model.types(),
                           current_district=district,
                           current_type=hospital_type,
                           search=search,
                           page=page,
                           per_page=per_page,
                           total=total,
                           total_pages=(total + per_page - 1) // per_page)


@hospitals_bp.route('/<int:hospital_id>')
@login_required
def hospital_detail(hospital_id):
    """Show hospital detail page."""
    hospital_dict = hospital_model.get(hospital_id)

    if not hospital_dict:
        return "Hospital not found", 404

    # Get nearby hospitals in the same district with coordinates
    nearby_list = hospital_model.nearby(hospital_dict['district'], hospital_id)

    return render_template('hospitals/detail.html', hospital=hospital_dict, nearby_hospitals=nearby_list)


@hospitals_bp.route('/api')
@login_required
def api_hospitals():
    """API endpoint for hospital data."""
    # Get query parameters
    district = request.args.get('district', '')
    hospital_type = request.args.get('type', '')
    search = request.args.get('search', '')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    hospitals = hospital_model.list_paginated(district, hospital_type, search, per_page=limit, offset=offset)

    return jsonify({
        'hospitals': hospitals,
        'count': len(hospitals)
    })


@hospitals_bp.route('/api/districts')
@login_required
def api_districts():
    """API endpoint for list of districts."""
    return jsonify({'districts': hospital_model.districts()})


@hospitals_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for hospital statistics."""
    stats = hospital_model.stats()
    return jsonify({
        'total': stats['total'],
        'by_district': stats['by_district'],
        'by_type': stats['by_type']
    })