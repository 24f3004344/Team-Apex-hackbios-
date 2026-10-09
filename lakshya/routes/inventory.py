from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from db import get_db

inventory_bp = Blueprint("inventory", __name__)


# =====================================================================
# INVENTORY ROUTES: MEDICINES & DIAGNOSTICS
# =====================================================================

@inventory_bp.route("/inventory")
def inventory_page():
    """Live Medicine & Diagnostic Tests Inventory Management."""
    db = get_db()
    medicines = db.execute("SELECT * FROM medicines ORDER BY stock_status ASC, name ASC").fetchall()
    diagnostics = db.execute("SELECT * FROM diagnostics ORDER BY tier ASC, test_name ASC").fetchall()
    return render_template("inventory.html", medicines=medicines, diagnostics=diagnostics)


@inventory_bp.route("/api/medicine/<int:med_id>/update", methods=["POST"])
def api_medicine_update(med_id):
    """Update medicine stock quantity and status."""
    data = request.get_json() or {}
    units = data.get("units")
    stock_status = data.get("stock_status", "").strip()

    db = get_db()
    existing = db.execute("SELECT id FROM medicines WHERE id = ?", (med_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    updates, params = [], []
    if units is not None:
        units = int(units)
        updates.append("units = ?")
        params.append(units)
        # Auto-compute stock_status from units if not explicitly provided
        if not stock_status:
            if units == 0:
                stock_status = "Out of Stock"
            elif units < 50:
                stock_status = "Low Stock"
            else:
                stock_status = "Available"

    if stock_status:
        if stock_status not in ("Available", "Low Stock", "Out of Stock"):
            return jsonify({"success": False, "error": "Invalid stock_status"}), 400
        updates.append("stock_status = ?")
        params.append(stock_status)

    updates.append("last_updated = ?")
    params.append(datetime.now().strftime("%d %b %Y, %I:%M %p"))

    if updates:
        params.append(med_id)
        db.execute(f"UPDATE medicines SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()

    return jsonify({"success": True, "message": f"Medicine #{med_id} stock updated"})


@inventory_bp.route("/api/medicine/<int:med_id>/delete", methods=["POST"])
def api_medicine_delete(med_id):
    """Delete a medicine entry from inventory."""
    db = get_db()
    existing = db.execute("SELECT id FROM medicines WHERE id = ?", (med_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    db.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    db.commit()
    return jsonify({"success": True, "message": f"Medicine #{med_id} removed from inventory"})


@inventory_bp.route("/api/medicine-search")
def api_medicine_search():
    """Live search API for medicines by name, category, and district."""
    query = request.args.get("q", "").strip()
    district = request.args.get("district", "").strip()

    db = get_db()
    sql = "SELECT * FROM medicines WHERE 1=1"
    params = []
    if query:
        sql += " AND (name LIKE ? OR category LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if district:
        sql += " AND district LIKE ?"
        params.append(f"%{district}%")
    sql += " LIMIT 15"
    results = [dict(row) for row in db.execute(sql, params).fetchall()]

    return jsonify({"success": True, "count": len(results), "medicines": results})

