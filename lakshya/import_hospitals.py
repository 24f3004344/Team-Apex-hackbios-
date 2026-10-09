#!/usr/bin/env python3
"""
Script to fetch hospital data from https://govthealth.cg.gov.in/sna/AllHospitals.aspx
and store it in the SQLite database.
"""
import re
import sqlite3
import os

# Database path
DATABASE = os.path.join(os.path.dirname(__file__), "swasthya.db")

def extract_hospital_data():
    """Extract hospital data from the saved HTML file."""
    html_file = '/var/folders/c1/1jc_nv1x3913y18ppfmtlhqc0000gn/T/1791548923507-copilot-tool-output-696d930b768c47679c7bf9f8795d1a3a.txt'
    
    with open(html_file, 'r') as f:
        content = f.read()
    
    # Find all td content
    td_pattern = r'<td[^>]*>(.*?)</td>'
    matches = re.findall(td_pattern, content, re.DOTALL)
    
    # Each row has 8 columns: Sno, District, Hospital Type, Hospital Name, Address, Phone1, Phone2, Email
    rows = len(matches) // 8
    hospitals = []
    
    for i in range(rows):
        row_data = []
        for j in range(8):
            idx = i * 8 + j
            if idx < len(matches):
                clean = re.sub(r'<[^>]+>', '', matches[idx]).strip()
                row_data.append(clean)
        
        if len(row_data) == 8:
            hospitals.append({
                'sno': row_data[0],
                'district': row_data[1],
                'hospital_type': row_data[2],
                'hospital_name': row_data[3],
                'address': row_data[4],
                'phone1': row_data[5],
                'phone2': row_data[6],
                'email': row_data[7]
            })
    
    return hospitals

def create_hospitals_table():
    """Create the hospitals table in the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sno TEXT,
            district TEXT NOT NULL,
            hospital_type TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            address TEXT,
            phone1 TEXT,
            phone2 TEXT,
            email TEXT,
            state TEXT DEFAULT 'Chhattisgarh',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_district ON hospitals(district)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_type ON hospitals(hospital_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_name ON hospitals(hospital_name)")
    
    conn.commit()
    conn.close()
    print("Hospitals table created successfully")

def import_hospitals(hospitals):
    """Import hospital data into the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clear existing data (optional - comment out if you want to keep existing)
    cursor.execute("DELETE FROM hospitals")
    
    inserted = 0
    for hospital in hospitals:
        try:
            cursor.execute("""
                INSERT INTO hospitals (sno, district, hospital_type, hospital_name, address, phone1, phone2, email, state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hospital['sno'],
                hospital['district'],
                hospital['hospital_type'],
                hospital['hospital_name'],
                hospital['address'],
                hospital['phone1'],
                hospital['phone2'],
                hospital['email'],
                'Chhattisgarh'
            ))
            inserted += 1
        except sqlite3.Error as e:
            print(f"Error inserting hospital {hospital['hospital_name']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"Successfully imported {inserted} hospitals")

def verify_import():
    """Verify the imported data."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM hospitals")
    total = cursor.fetchone()[0]
    print(f"\nTotal hospitals in database: {total}")
    
    # By district
    cursor.execute("""
        SELECT district, COUNT(*) as count 
        FROM hospitals 
        GROUP BY district 
        ORDER BY count DESC
    """)
    print("\nHospitals by district:")
    for row in cursor.fetchall():
        print(f"  {row['district']}: {row['count']}")
    
    # By hospital type
    cursor.execute("""
        SELECT hospital_type, COUNT(*) as count 
        FROM hospitals 
        GROUP BY hospital_type 
        ORDER BY count DESC
    """)
    print("\nHospitals by type:")
    for row in cursor.fetchall():
        print(f"  {row['hospital_type']}: {row['count']}")
    
    # Sample records
    cursor.execute("SELECT * FROM hospitals LIMIT 5")
    print("\nSample records:")
    for row in cursor.fetchall():
        print(f"  {row['hospital_name']} - {row['district']} - {row['hospital_type']}")
    
    conn.close()

def main():
    print("=" * 60)
    print("Hospital Data Import Script")
    print("=" * 60)
    
    # Extract data
    print("\n1. Extracting hospital data from website...")
    hospitals = extract_hospital_data()
    print(f"   Extracted {len(hospitals)} hospitals")
    
    # Create table
    print("\n2. Creating hospitals table...")
    create_hospitals_table()
    
    # Import data
    print("\n3. Importing hospitals into database...")
    import_hospitals(hospitals)
    
    # Verify
    print("\n4. Verifying import...")
    verify_import()
    
    print("\n" + "=" * 60)
    print("Import completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()