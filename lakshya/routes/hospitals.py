"""
Hospital routes for accessing government hospital data.
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from db import get_db

hospitals_bp = Blueprint('hospitals', __name__, url_prefix='/hospitals')


def get_nearby_hospitals(district, exclude_id, limit=5):
    """Get nearby hospitals in the same district."""
    db = get_db()
    hospitals = db.execute(
        "SELECT id, hospital_name, hospital_type, phone1 FROM hospitals WHERE district = ? AND id != ? ORDER BY hospital_name LIMIT ?",
        (district, exclude_id, limit)
    ).fetchall()
    return hospitals


# Make helper available in templates
@hospitals_bp.app_template_global()
def get_nearby_hospitals_global(district, exclude_id, limit=5):
    """Template global for getting nearby hospitals."""
    return get_nearby_hospitals(district, exclude_id, limit)


@hospitals_bp.route('/')
def list_hospitals():
    """List all hospitals with pagination and filtering."""
    db = get_db()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    district = request.args.get('district', '')
    hospital_type = request.args.get('type', '')
    search = request.args.get('search', '')
    
    # Build query
    query = "SELECT * FROM hospitals WHERE 1=1"
    params = []
    
    if district:
        query += " AND district = ?"
        params.append(district)
    
    if hospital_type:
        query += " AND hospital_type = ?"
        params.append(hospital_type)
    
    if search:
        query += " AND (hospital_name LIKE ? OR address LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    # Get total count
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = db.execute(count_query, params).fetchone()[0]
    
    # Add pagination
    query += " ORDER BY district, hospital_name LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    hospitals = db.execute(query, params).fetchall()
    
    # Convert Row objects to dicts for JSON serialization
    hospitals_list = [dict(h) for h in hospitals]
    
    # Fetch up to 150 matching hospitals with coordinates for interactive map rendering
    map_query = "SELECT id, sno, district, hospital_type, hospital_name, address, phone1, phone2, email, latitude, longitude FROM hospitals WHERE 1=1"
    map_params = []
    if district:
        map_query += " AND district = ?"
        map_params.append(district)
    if hospital_type:
        map_query += " AND hospital_type = ?"
        map_params.append(hospital_type)
    if search:
        map_query += " AND (hospital_name LIKE ? OR address LIKE ?)"
        map_params.extend([f"%{search}%", f"%{search}%"])
    map_query += " AND latitude IS NOT NULL AND longitude IS NOT NULL ORDER BY district, hospital_name LIMIT 150"
    map_hospitals = [dict(h) for h in db.execute(map_query, map_params).fetchall()]
    
    # Get unique districts and types for filters
    districts = db.execute("SELECT DISTINCT district FROM hospitals ORDER BY district").fetchall()
    types = db.execute("SELECT DISTINCT hospital_type FROM hospitals ORDER BY hospital_type").fetchall()
    
    return render_template('hospitals/list.html',
                           hospitals=hospitals_list,
                           map_hospitals=map_hospitals,
                           districts=[d['district'] for d in districts],
                           types=[t['hospital_type'] for t in types],
                           current_district=district,
                           current_type=hospital_type,
                           search=search,
                           page=page,
                           per_page=per_page,
                           total=total,
                           total_pages=(total + per_page - 1) // per_page)


@hospitals_bp.route('/<int:hospital_id>')
def hospital_detail(hospital_id):
    """Show hospital detail page."""
    db = get_db()
    hospital = db.execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,)).fetchone()
    
    if not hospital:
        return "Hospital not found", 404
    
    # Convert to dict for JSON serialization
    hospital_dict = dict(hospital)
    
    # Get nearby hospitals in the same district with coordinates
    nearby = db.execute(
        "SELECT id, hospital_name, hospital_type, district, address, phone1, latitude, longitude FROM hospitals WHERE district = ? AND id != ? ORDER BY hospital_name LIMIT 6",
        (hospital['district'], hospital_id)
    ).fetchall()
    nearby_list = [dict(h) for h in nearby]
    
    return render_template('hospitals/detail.html', hospital=hospital_dict, nearby_hospitals=nearby_list)


@hospitals_bp.route('/api')
def api_hospitals():
    """API endpoint for hospital data."""
    db = get_db()
    
    # Get query parameters
    district = request.args.get('district', '')
    hospital_type = request.args.get('type', '')
    search = request.args.get('search', '')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Build query
    query = "SELECT * FROM hospitals WHERE 1=1"
    params = []
    
    if district:
        query += " AND district = ?"
        params.append(district)
    
    if hospital_type:
        query += " AND hospital_type = ?"
        params.append(hospital_type)
    
    if search:
        query += " AND (hospital_name LIKE ? OR address LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    query += " ORDER BY district, hospital_name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    hospitals = db.execute(query, params).fetchall()
    
    return jsonify({
        'hospitals': [dict(h) for h in hospitals],
        'count': len(hospitals)
    })


@hospitals_bp.route('/api/districts')
def api_districts():
    """API endpoint for list of districts."""
    db = get_db()
    districts = db.execute("SELECT DISTINCT district FROM hospitals ORDER BY district").fetchall()
    return jsonify({'districts': [d['district'] for d in districts]})


@hospitals_bp.route('/api/stats')
def api_stats():
    """API endpoint for hospital statistics."""
    db = get_db()
    
    # Total hospitals
    total = db.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
    
    # By district
    by_district = db.execute("""
        SELECT district, COUNT(*) as count 
        FROM hospitals 
        GROUP BY district 
        ORDER BY count DESC
    """).fetchall()
    
    # By type
    by_type = db.execute("""
        SELECT hospital_type, COUNT(*) as count 
        FROM hospitals 
        GROUP BY hospital_type 
        ORDER BY count DESC
    """).fetchall()
    
    return jsonify({
        'total': total,
        'by_district': [dict(d) for d in by_district],
        'by_type': [dict(t) for t in by_type]
    })