from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import re

# Room prefix → building key mapping
ROOM_BUILDING_MAP = {
    'DB': 'dharithri', 'DA': 'dharithri',
    'A':  'main_block', 'B': 'main_block',
    'C':  'main_block', 'D': 'main_block',
    'E':  'main_block', 'F': 'main_block',
    'G':  'main_block'
}

# Building entrance GPS coordinates
# ✅ VERIFIED VIIT Duvvada exact location
BUILDING_COORDS = {
    # Main entrance gate
    'main_gate':      (17.712169, 83.164343),
    # Dharithri Block (main academic hub)
    'dharithri':      (17.710005, 83.167195),
    # Vignan's Main Block (cross-shaped)
    'main_block':     (17.710474, 83.165917),
    # Vignan Institute of Pharmaceutical Tech
    'pharmacy':       (17.711949, 83.164173),
    # Girls Hostel
    'hostel':         (17.705491, 83.165945),
    
    # Other campus points (approximate shifts from main)
    'cricket_ground': (17.711100, 83.164500),
    'new_block':      (17.710500, 83.168000),
    'atm':            (17.711800, 83.164800),
    'parking':        (17.711500, 83.165500),
    'student_parking': (17.709500, 83.166500),
}

def get_dest_coords(location_name, loc_id=""):
    """Return (lat, lng, is_indoor) for a given location name."""
    name_upper = location_name.upper().strip()
    id_upper = loc_id.upper().strip()

    # Check if it's an indoor room (starts with known prefix)
    for prefix, building in ROOM_BUILDING_MAP.items():
        if name_upper.startswith(prefix + '-') or name_upper.startswith(prefix + ' ') or \
           id_upper.startswith(prefix + '-') or id_upper.startswith(prefix + ' '):
            coords = BUILDING_COORDS.get(building, (17.7718, 83.2288))
            return coords[0], coords[1], True

    # Outdoor/building-level locations — match by keyword
    if 'DHARITHRI' in name_upper:
        c = BUILDING_COORDS['dharithri']
    elif 'CRICKET' in name_upper:
        c = BUILDING_COORDS['cricket_ground']
    elif 'PHARMACY' in name_upper:
        c = BUILDING_COORDS['pharmacy']
    elif 'HOSTEL' in name_upper:
        c = BUILDING_COORDS['hostel']
    elif 'NEW BLOCK' in name_upper:
        c = BUILDING_COORDS['new_block']
    elif 'ATM' in name_upper:
        c = BUILDING_COORDS['atm']
    elif 'STUDENT PARKING' in name_upper:
        c = BUILDING_COORDS['student_parking']
    elif 'PARKING' in name_upper:
        c = BUILDING_COORDS['parking']
    elif 'MAIN GATE' in name_upper:
        c = BUILDING_COORDS['main_gate']
    else:
        c = BUILDING_COORDS['main_block']

    return c[0], c[1], False


def get_floor_svg_name(room_id):
    """Returns SVG filename suffix based on room floor number."""
    room_upper = room_id.upper()
    # Extract floor number from room ID
    # DB-01..09 = ground, DB-11..19 = floor 1, etc.
    if re.search(r'[A-Z]+-0', room_upper):
        return 'gf'
    elif re.search(r'[A-Z]+-1', room_upper):
        return 'f1'
    elif re.search(r'[A-Z]+-2', room_upper):
        return 'f2'
    elif re.search(r'[A-Z]+-3', room_upper):
        return 'f3'
    elif re.search(r'[A-Z]+-4', room_upper):
        return 'f4'
    return 'gf'

def get_wing(room_id):
    return 'Left (DB)' if room_id.upper().startswith('DB') else 'Right (DA)'


app = Flask(__name__)
APP_TITLE = "VIIT Campus Navigation – Vignan's Institute of Information Technology"

def get_locations():
    return pd.read_csv("map_urls.csv").to_dict('records')

@app.route('/')
def index():
    locations = get_locations()
    return render_template('index.html', title=APP_TITLE, locations=locations)

@app.route('/location/<loc_id>')
def detail(loc_id):
    df = pd.read_csv("map_urls.csv")
    location = df[df['id'] == loc_id].to_dict('records')
    if not location:
        return redirect(url_for('index'))
    
    loc = location[0]
    # Split directions into a list for the numbered list requirement
    steps = loc['directions'].split(' → ')
    
    dest_lat, dest_lng, is_indoor = get_dest_coords(loc['name'], loc['id'])
    
    floor_svg_name = get_floor_svg_name(loc['id']) if is_indoor else None
    wing = get_wing(loc['id']) if is_indoor else None
    floor_num = {'gf': 0, 'f1': 1, 'f2': 2, 'f3': 3, 'f4': 4}.get(floor_svg_name or 'gf', 0)

    return render_template('location.html',
        title=APP_TITLE,
        name=loc['name'],
        description=loc['description'],
        steps=steps,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        is_indoor=is_indoor,
        floor_svg_name=floor_svg_name,
        floor=floor_num,
        wing=wing,
        id=loc['id']
    )

# Legacy route for compatibility if needed, but we'll use /location/<id>
@app.route('/result', methods=["GET", 'POST'])
def result():
    id = request.form.get('destination') or request.args.get('id')
    if id:
        return redirect(url_for('detail', loc_id=id))
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
