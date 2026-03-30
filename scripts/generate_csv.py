import csv
import os

# Coordinates Mapping
COORDS = {
    "Main Gate": (17.7714, 83.2284),
    "Dharithri": (17.7720, 83.2282),
    "Main Block": (17.7712, 83.2293),
    "Cricket Ground": (17.7716, 83.2284),
    "Pharmacy College": (17.7705, 83.2274),
    "Girls Hostel": (17.7725, 83.2295),
    "Student Parking": (17.7710, 83.2275),
    "New Block": (17.7728, 83.2285),
    "ATM": (17.7710, 83.2275), # Near Student Parking
    "Football Ground": (17.7720, 83.2278), # Approx near Dharithri West
    "Pharmacy": (17.7705, 83.2274),
}

ORIGIN_COORDS = "My+Location" 

# Data for VIIT Locations
locations = [
    # CAMPUS-LEVEL LOCATIONS
    {"id": "VIIT-G-01", "name": "Main Gate", "description": "VIIT Campus Main Entrance", "block": "Campus", "floor": "0", "type": "Gate", "position": "Main Entrance", "coord_key": "Main Gate"},
    {"id": "VIIT-B-01", "name": "Dharithri Block", "description": "Main academic building (G+4 floors)", "block": "Dharithri", "floor": "0", "type": "Building", "position": "Center", "coord_key": "Dharithri"},
    {"id": "VIIT-S-01", "name": "Cricket Ground", "description": "Sports facility near Pharmacy College", "block": "Campus", "floor": "0", "type": "Sports", "position": "Near Pharmacy College", "coord_key": "Cricket Ground"},
    {"id": "VIIT-S-02", "name": "Football Ground", "description": "Near Dharithri Block west side", "block": "Campus", "floor": "0", "type": "Sports", "position": "West of Dharithri", "coord_key": "Football Ground"},
    {"id": "VIIT-P-01", "name": "Faculty Parking", "description": "Parking area near Dharithri Block", "block": "Campus", "floor": "0", "type": "Parking", "position": "Near Dharithri", "coord_key": "Dharithri"},
    {"id": "VIIT-B-02", "name": "New Block", "description": "New academic block (under construction)", "block": "Campus", "floor": "0", "type": "Building", "position": "Under Construction", "coord_key": "New Block"},
    {"id": "VIIT-B-03", "name": "Pharmacy College", "description": "Separate pharmacy college building", "block": "Campus", "floor": "0", "type": "Building", "position": "Separate Building", "coord_key": "Pharmacy College"},
    {"id": "VIIT-H-01", "name": "Girls Hostel", "description": "Girls hostel near campus north", "block": "Campus", "floor": "0", "type": "Hostel", "position": "Campus North", "coord_key": "Girls Hostel"},
    {"id": "VIIT-A-01", "name": "ATM", "description": "ATM near student parking", "block": "Campus", "floor": "0", "type": "Facility", "position": "Near Student Parking", "coord_key": "ATM"},
    {"id": "VIIT-P-02", "name": "Student Parking", "description": "Student parking near campus south", "block": "Campus", "floor": "0", "type": "Parking", "position": "Campus South", "coord_key": "Student Parking"},

    # DHARITHRI BLOCK - GROUND FLOOR
    {"id": "DB-01", "name": "Physics Lab", "description": "Ground Floor - Dharithri Block Left Wing", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-02", "name": "Engineering Drawing Hall-2", "description": "Ground Floor - Left Wing", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-04", "name": "Chemistry Lab", "description": "Ground Floor - Left Wing (BSH)", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Left Wing (BSH)", "coord_key": "Dharithri"},
    {"id": "DA-02(A)", "name": "Applied Physics Lab", "description": "Ground Floor - Right Wing", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-02(B)", "name": "Dark Room Physics Lab", "description": "Ground Floor - Right Wing", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-03", "name": "Engineering Drawing Hall-1", "description": "Ground Floor - Right Wing", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "FT-L", "name": "Functional Thin Films Lab", "description": "Ground Floor - Left Wing far end", "block": "Dharithri", "floor": "0", "type": "Lab", "position": "Left Wing far end", "coord_key": "Dharithri"},

    # DHARITHRI BLOCK - FIRST FLOOR
    {"id": "DB-11", "name": "Lecture Hall", "description": "1st Floor - Left Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-12", "name": "Lecture Hall", "description": "1st Floor - Left Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-13", "name": "Lecture Hall", "description": "1st Floor - Left Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-14", "name": "Lecture Hall", "description": "1st Floor - Left Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DA-11", "name": "Lecture Hall", "description": "1st Floor - Right Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-12", "name": "Lecture Hall", "description": "1st Floor - Right Wing (BSH HOD Room)", "block": "Dharithri", "floor": "1", "type": "Office", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-13", "name": "Lecture Hall", "description": "1st Floor - Right Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-14", "name": "Lecture Hall", "description": "1st Floor - Right Wing", "block": "Dharithri", "floor": "1", "type": "Lecture Hall", "position": "Right Wing", "coord_key": "Dharithri"},

    # DHARITHRI BLOCK - SECOND FLOOR
    {"id": "DA-22", "name": "Dean Admin Office", "description": "2nd Floor - Right Wing", "block": "Dharithri", "floor": "2", "type": "Office", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-27", "name": "Seminar Hall", "description": "2nd Floor - Right Wing center", "block": "Dharithri", "floor": "2", "type": "Lab", "position": "Right Wing center", "coord_key": "Dharithri"},
    {"id": "DB-21", "name": "Lecture Hall", "description": "2nd Floor - Left Wing", "block": "Dharithri", "floor": "2", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-22", "name": "Lecture Hall", "description": "2nd Floor - Left Wing", "block": "Dharithri", "floor": "2", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-23", "name": "Lecture Hall", "description": "2nd Floor - Left Wing", "block": "Dharithri", "floor": "2", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-24", "name": "Lecture Hall", "description": "2nd Floor - Left Wing", "block": "Dharithri", "floor": "2", "type": "Lecture Hall", "position": "Left Wing", "coord_key": "Dharithri"},

    # DHARITHRI BLOCK - THIRD FLOOR
    {"id": "DB-31", "name": "English Communication Skill Lab", "description": "3rd Floor - Left Wing", "block": "Dharithri", "floor": "3", "type": "Lab", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-37", "name": "Bill Gates Lab", "description": "3rd Floor - Left Wing center", "block": "Dharithri", "floor": "3", "type": "Lab", "position": "Left Wing center", "coord_key": "Dharithri"},
    {"id": "DA-38", "name": "Sergey Brain Lab", "description": "3rd Floor - Right Wing", "block": "Dharithri", "floor": "3", "type": "Lab", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DA-33", "name": "MBA Staff Room", "description": "3rd Floor - Right Wing", "block": "Dharithri", "floor": "3", "type": "Office", "position": "Right Wing", "coord_key": "Dharithri"},

    # DHARITHRI BLOCK - FOURTH FLOOR
    {"id": "DB-41", "name": "Steve Jobs Lab", "description": "4th Floor - Left Wing", "block": "Dharithri", "floor": "4", "type": "Lab", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-48", "name": "MCA HOD Room", "description": "4th Floor - Left Wing", "block": "Dharithri", "floor": "4", "type": "Office", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-49", "name": "Breandan Eich Lab", "description": "4th Floor - Left Wing", "block": "Dharithri", "floor": "4", "type": "Lab", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DA-09", "name": "OMS Skill Centre of Excellence", "description": "4th Floor - Right Wing", "block": "Dharithri", "floor": "4", "type": "Office", "position": "Right Wing", "coord_key": "Dharithri"},
    {"id": "DB-45(A)", "name": "PG Library", "description": "4th Floor - Left Wing", "block": "Dharithri", "floor": "4", "type": "Library", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "DB-46", "name": "Research Lab", "description": "4th Floor - Left Wing", "block": "Dharithri", "floor": "4", "type": "Lab", "position": "Left Wing", "coord_key": "Dharithri"},
    {"id": "CEER", "name": "CEER Department", "description": "4th Floor - Dharithri Block", "block": "Dharithri", "floor": "4", "type": "Office", "position": "Main Block", "coord_key": "Dharithri"},
    {"id": "DB-44A", "name": "IT Department", "description": "4th Floor - Left Wing", "block": "Dharithri", "floor": "4", "type": "Office", "position": "Left Wing", "coord_key": "Dharithri"},

    # VIGNAN'S MAIN BLOCK
    {"id": "VA-01", "name": "Vayu Block", "description": "NW Wing - Main Block", "block": "Main Block", "floor": "1", "type": "Building", "wing": "NW Wing", "coord_key": "Main Block"},
    {"id": "PB-01", "name": "Prudhvi Block", "description": "North Wing - Main Block", "block": "Main Block", "floor": "1", "type": "Building", "wing": "North Wing", "coord_key": "Main Block"},
    {"id": "TB-01", "name": "Teja Block", "description": "Center Wing - Main Block", "block": "Main Block", "floor": "1", "type": "Building", "wing": "Center Wing", "coord_key": "Main Block"},
    {"id": "VB-01", "name": "Varun Block", "description": "NE Wing - Main Block", "block": "Main Block", "floor": "1", "type": "Building", "wing": "NE Wing", "coord_key": "Main Block"},
    {"id": "AB-01", "name": "Aakash Block", "description": "SW Wing - Main Block", "block": "Main Block", "floor": "1", "type": "Building", "wing": "SW Wing", "coord_key": "Main Block"},
    {"id": "AG-01", "name": "Agni Block", "description": "SE Wing - Main Block", "block": "Main Block", "floor": "1", "type": "Building", "wing": "SE Wing", "coord_key": "Main Block"},
    {"id": "G-CY", "name": "G-Block Courtyard", "description": "Central courtyard open to sky", "block": "Main Block", "floor": "0", "type": "Facility", "wing": "G-Block", "coord_key": "Main Block"},
    {"id": "G-03", "name": "Invention Center", "description": "3rd Floor G-Block", "block": "Main Block", "floor": "3", "type": "Lab", "wing": "G-Block", "coord_key": "Main Block"},
    {"id": "G-04", "name": "Abdul Kalam Center", "description": "4th Floor G-Block", "block": "Main Block", "floor": "4", "type": "Lab", "wing": "G-Block", "coord_key": "Main Block"},
    {"id": "VB-32", "name": "Vayu B-32 Research Lab", "description": "3rd Floor Vayu Block", "block": "Main Block", "floor": "3", "type": "Lab", "wing": "Vayu Block", "coord_key": "Main Block"},
    {"id": "VB-34", "name": "Vayu B-34 IQAC Office", "description": "3rd Floor Vayu Block", "block": "Main Block", "floor": "3", "type": "Office", "wing": "Vayu Block", "coord_key": "Main Block"},
    {"id": "PB-32", "name": "Prudhvi C-32 Power System Lab", "description": "3rd Floor Prudhvi Block", "block": "Main Block", "floor": "3", "type": "Lab", "wing": "Prudhvi Block", "coord_key": "Main Block"},
    {"id": "TB-32", "name": "Teja D-32 Digital Nano Acquisition Lab", "description": "3rd Floor Teja Block", "block": "Main Block", "floor": "3", "type": "Lab", "wing": "Teja Block", "coord_key": "Main Block"},
    {"id": "TB-35", "name": "Teja D-35 Goduca Lab", "description": "3rd Floor Teja Block", "block": "Main Block", "floor": "3", "type": "Lab", "wing": "Teja Block", "coord_key": "Main Block"},
    {"id": "AG-31", "name": "Agni F-31 Mech Staff Room", "description": "3rd Floor Agni Block", "block": "Main Block", "floor": "3", "type": "Office", "wing": "Agni Block", "coord_key": "Main Block"},
    {"id": "AM-04", "name": "Computer Programming Hall", "description": "4th Floor Aakash Block", "block": "Main Block", "floor": "4", "type": "Lab", "wing": "Aakash Block", "coord_key": "Main Block"},
    {"id": "EF-04", "name": "Drawing Hall", "description": "4th Floor Varun Block", "block": "Main Block", "floor": "4", "type": "Lab", "wing": "Varun Block", "coord_key": "Main Block"},
]

embed_url_base = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3800.7244110041142!2d83.16591749999998!3d17.7104743!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3a3968cb428b8087%3A0xaa3e198c43836a65!2sVignan's%20Institute%20Of%20Information%20Technology!5e0!3m2!1sen!2sin!4v1773767014835!5m2!1sen!2sin"

def generate_directions_text(loc):
    block = loc.get('block', '')
    id = loc.get('id', '')
    name = loc.get('name', '')
    floor = loc.get('floor', '0')
    pos = loc.get('position', '')
    
    if block == "Dharithri":
        if id.startswith("DB"):
            return f"Enter Dharithri Block → Take staircase/lift to Floor {floor} → Turn LEFT at the corridor → {name} is {pos}"
        elif id.startswith("DA"):
            return f"Enter Dharithri Block → Take staircase/lift to Floor {floor} → Turn RIGHT at the corridor → {name} is {pos}"
        else:
            return f"Enter Dharithri Block → Follow signs to {name}"
    
    elif block == "Main Block":
        wing = loc.get('wing', 'Main Wing')
        side = "left" if "Left" in pos else "right" 
        return f"Enter VIIT Main Block from the courtyard → Walk towards {wing} → Take stairs to Floor {floor} → {name} is on the {side}"
    
    else:
        return f"Locate {name} at {pos} within the VIIT Campus Area."

def get_directions_url(loc):
    key = loc.get('coord_key', 'Main Gate')
    lat, lng = COORDS.get(key, COORDS["Main Gate"])
    dest = f"{lat},{lng}"
    return f"https://www.google.com/maps/dir/?api=1&origin={ORIGIN_COORDS}&destination={dest}&travelmode=walking"

# Prepare CSV rows
rows = []
for loc in locations:
    row = {
        "id": loc['id'],
        "name": loc['name'],
        "description": loc['description'],
        "block": loc['block'],
        "floor": loc['floor'],
        "type": loc['type'],
        "directions": generate_directions_text(loc),
        "map_embed_url": embed_url_base,
        "map_directions_url": get_directions_url(loc)
    }
    rows.append(row)

# Write to CSV
csv_file = "map_urls.csv"
fieldnames = ["id", "name", "description", "block", "floor", "type", "directions", "map_embed_url", "map_directions_url"]

with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully generated {csv_file} with {len(rows)} entries and walking routes.")
