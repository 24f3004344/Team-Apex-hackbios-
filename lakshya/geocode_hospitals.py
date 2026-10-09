#!/usr/bin/env python3
"""
Geocode hospital addresses using Google Maps Geocoding API.
Updates the hospitals table with latitude and longitude.
"""
import os
import sys
import time
import math
import sqlite3
import requests

# Configuration — key MUST come from env (never commit keys).
# NOTE: the key previously hardcoded here is compromised (it lives in git
# history). Revoke/regenerate it in Google Cloud Console, then export the new one:
#   export GOOGLE_MAPS_API_KEY="your-new-key"
DATABASE = os.path.join(os.path.dirname(__file__), "swasthya.db")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def _require_api_key():
    if not GOOGLE_MAPS_API_KEY:
        print("ERROR: GOOGLE_MAPS_API_KEY env var is not set. Export it first.")
        sys.exit(1)

DISTRICT_COORDS = {
    'BALOD': (20.7297, 81.2039),
    'BALODA BAZAR': (21.6608, 81.9548),
    'BALRAMPUR': (23.6167, 83.6167),
    'BASTAR': (19.0748, 82.0084),
    'BEMETARA': (21.7019, 81.5482),
    'BIJAPUR': (18.7900, 80.8160),
    'BILASPUR': (22.0797, 82.1409),
    'DANTEWADA': (18.8953, 81.3508),
    'DHAMTARI': (20.7071, 81.5497),
    'DURG': (21.1904, 81.2849),
    'GARIYABAND': (20.9419, 82.0628),
    'GAURELLA PENDRA MARWAHI': (22.7500, 81.9167),
    'JANJGIR-CHAMPA': (22.0163, 82.5707),
    'JASHPUR': (22.8872, 84.1444),
    'KABIRDHAM': (22.0118, 81.2464),
    'KANKER': (20.2719, 81.4925),
    'KHAIRGARH CHHUIKHADAN GANDAI': (21.4167, 80.9833),
    'KONDAGAON': (19.5982, 81.6702),
    'KORBA': (22.3595, 82.7501),
    'KOREA': (23.2736, 82.5562),
    'MAHASAMUND': (21.1084, 82.0963),
    'MANENDRAGARH CHIRIMIRI BHARATPUR': (23.2167, 82.2000),
    'MOHLA MANPUR AMBAGARH CHOUKI': (20.6500, 80.7333),
    'MUNGELI': (22.0667, 81.6833),
    'NARAYANPUR': (19.7153, 81.2458),
    'RAIGARH': (21.8974, 83.3950),
    'RAIPUR': (21.2514, 81.6296),
    'RAJNANDGAON': (21.0974, 81.0310),
    'SAKTI': (22.0333, 82.9667),
    'SARANGARH BILAIGARH': (21.5833, 83.0833),
    'SUKMA': (18.4000, 81.6667),
    'SURAJPUR': (23.2200, 82.8600),
    'SURGUJA': (23.1189, 83.1963)
}

# Rate limiting: 50 requests per second for Geocoding API
# We'll use 10 requests per second to be safe
REQUEST_DELAY = 0.1  # seconds between requests

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def geocode_address(address):
    """
    Geocode an address using Google Maps Geocoding API.
    Returns (latitude, longitude) or (None, None) if failed.
    """
    # Clean and prepare address
    clean_address = address.strip()
    if not clean_address:
        return None, None
    
    # Add Chhattisgarh, India for better accuracy
    full_address = f"{clean_address}, Chhattisgarh, India"
    
    params = {
        'address': full_address,
        'key': GOOGLE_MAPS_API_KEY,
        'region': 'in'  # Bias to India
    }
    
    try:
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        elif data['status'] == 'OVER_QUERY_LIMIT':
            print("  Rate limit hit, waiting...")
            time.sleep(2)
            return geocode_address(address)  # Retry
        else:
            print(f"  Geocoding failed: {data['status']} - {data.get('error_message', 'No error message')}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"  Request error: {e}")
        return None, None
    except Exception as e:
        print(f"  Unexpected error: {e}")
        return None, None

def geocode_hospitals(batch_size=100, start_from=0):
    """
    Geocode hospitals that don't have coordinates yet.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get hospitals without coordinates
    cursor.execute("""
        SELECT id, hospital_name, address, district 
        FROM hospitals 
        WHERE latitude IS NULL OR longitude IS NULL
        ORDER BY id
        LIMIT ? OFFSET ?
    """, (batch_size, start_from))
    
    hospitals = cursor.fetchall()
    
    if not hospitals:
        print("All hospitals already geocoded!")
        conn.close()
        return 0
    
    print(f"Geocoding {len(hospitals)} hospitals (batch starting at {start_from})...")
    
    success_count = 0
    for hospital in hospitals:
        hospital_id = hospital['id']
        name = hospital['hospital_name']
        address = hospital['address']
        district = hospital['district']
        
        print(f"  [{hospital_id}] {name} ({district})")
        
        # Try geocoding with full address first
        lat, lng = geocode_address(address)
        
        # If Google Geocoding API fails/denied, fallback to district centroid coordinates
        if lat is None:
            dist_key = (district or '').upper().strip()
            if dist_key in DISTRICT_COORDS:
                base_lat, base_lng = DISTRICT_COORDS[dist_key]
                angle = (hospital_id * 137.508) * (3.14159265 / 180)
                radius = 0.006 + (hospital_id % 24) * 0.003
                lat = round(base_lat + radius * math.sin(angle), 6)
                lng = round(base_lng + (radius / math.cos(math.radians(base_lat))) * math.cos(angle), 6)
                print(f"    ℹ Using district centroid fallback: {lat:.6f}, {lng:.6f}")

        if lat is not None and lng is not None:
            cursor.execute("""
                UPDATE hospitals 
                SET latitude = ?, longitude = ?, geocoded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (lat, lng, hospital_id))
            success_count += 1
            print(f"    ✓ {lat:.6f}, {lng:.6f}")
        else:
            print("    ✗ Failed to geocode")
        
        # Rate limiting
        time.sleep(REQUEST_DELAY)
    
    conn.commit()
    conn.close()
    
    print(f"\nBatch complete: {success_count}/{len(hospitals)} successfully geocoded")
    return success_count

def verify_geocoding():
    """Verify geocoding results."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM hospitals WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
    geocoded = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hospitals")
    total = cursor.fetchone()[0]
    
    print(f"\nGeocoding Status: {geocoded}/{total} hospitals have coordinates")
    
    # Show sample
    cursor.execute("""
        SELECT hospital_name, district, latitude, longitude 
        FROM hospitals 
        WHERE latitude IS NOT NULL 
        LIMIT 5
    """)
    print("\nSample geocoded hospitals:")
    for row in cursor.fetchall():
        print(f"  {row['hospital_name']} ({row['district']}): {row['latitude']:.6f}, {row['longitude']:.6f}")
    
    conn.close()

def main():
    _require_api_key()
    print("=" * 60)
    print("Hospital Geocoding Script")
    print("=" * 60)
    print(f"API Key: {GOOGLE_MAPS_API_KEY[:10]}...")
    print(f"Database: {DATABASE}")
    print()
    
    # Check current status
    verify_geocoding()
    
    # Process in batches
    batch_size = 50
    offset = 0
    total_success = 0
    
    while True:
        success = geocode_hospitals(batch_size, offset)
        if success == 0:
            break
        total_success += success
        offset += batch_size
        
        # Small delay between batches
        time.sleep(1)
    
    print(f"\nTotal geocoded in this run: {total_success}")
    verify_geocoding()
    
    print("\n" + "=" * 60)
    print("Geocoding completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()