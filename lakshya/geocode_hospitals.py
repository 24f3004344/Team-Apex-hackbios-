#!/usr/bin/env python3
"""
Geocode hospital addresses using Google Maps Geocoding API.
Updates the hospitals table with latitude and longitude.
"""
import os
import sys
import time
import sqlite3
import requests
from urllib.parse import quote

# Configuration
DATABASE = os.path.join(os.path.dirname(__file__), "swasthya.db")
GOOGLE_MAPS_API_KEY = "AIzaSyBCCOj8ob_JRXuuQA7qI-hVXTfn-jrSBl0"
GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

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
            print(f"  Rate limit hit, waiting...")
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
        
        # If failed, try with hospital name + district
        if lat is None:
            fallback_address = f"{name}, {district}, Chhattisgarh, India"
            print(f"    Retrying with: {fallback_address}")
            lat, lng = geocode_address(fallback_address)
        
        if lat is not None and lng is not None:
            cursor.execute("""
                UPDATE hospitals 
                SET latitude = ?, longitude = ?, geocoded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (lat, lng, hospital_id))
            success_count += 1
            print(f"    ✓ {lat:.6f}, {lng:.6f}")
        else:
            print(f"    ✗ Failed to geocode")
        
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