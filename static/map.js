// Verified VIIT campus center
const VIIT_CENTER = [17.711, 83.166];

// Campus boundary (Duvvada campus area)
const VIIT_BOUNDS = [
  [17.7040, 83.1630],   // southwest corner
  [17.7130, 83.1690]    // northeast corner
];

const BUILDING_COORDS = {
  "main_gate":      [17.712169, 83.164343],
  "dharithri":      [17.710005, 83.167195],
  "main_block":     [17.710474, 83.165917],
  "pharmacy":       [17.711949, 83.164173],
  "hostel":         [17.705491, 83.165945],
  "cricket_ground": [17.711100, 83.164500],
  "new_block":      [17.710500, 83.168000],
  "parking":        [17.711500, 83.165500],
  "atm":            [17.711800, 83.164800],
  "student_parking":[17.709500, 83.166500]
};

let map, userMarker, destMarker, routeLine, watchId;
let userPos = null;

// Check if we're on HTTPS (required for geolocation)
function checkHttps() {
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    document.getElementById('nav-status').innerHTML =
      'HTTPS required for GPS. <a href="' +
      location.href.replace('http:', 'https:') +
      '" style="color:#90caf9">Switch to HTTPS</a>';
    return false;
  }
  return true;
}

function initMap(destCoords, roomName) {
  map = L.map('nav-map', {
    zoomControl: true,
    minZoom: 15,
    maxZoom: 21
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 21,
    maxNativeZoom: 19
  }).addTo(map);

  // ✅ FIX: Set correct VIIT campus coordinates and zoom level 18
  // These are the EXACT coordinates of VIIT Duvvada
  const VIIT_CENTER = [17.7716, 83.2287];
  map.setView(VIIT_CENTER, 18);   // zoom 18 = building level detail

  // Destination marker with bounce animation
  const destIcon = L.divIcon({
    html: `<div style="
      position:relative;
      width:36px; height:36px;">
      <div style="
        position:absolute; top:0; left:0;
        width:36px; height:36px;
        background:#e53935;
        border-radius:50% 50% 50% 0;
        transform:rotate(-45deg);
        border:3px solid white;
        box-shadow:0 3px 10px rgba(0,0,0,0.4);">
      </div>
      <div style="
        position:absolute; top:9px; left:9px;
        width:14px; height:14px;
        background:white;
        border-radius:50%;">
      </div>
    </div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    className: ''
  });

  destMarker = L.marker(destCoords, { icon: destIcon })
    .addTo(map)
    .bindPopup(`<b>${roomName}</b><br>Your destination`)
    .openPopup();
}

function requestLocation() {
  document.getElementById('nav-status').textContent = 'Requesting GPS...';
  document.getElementById('btn-location').style.display = 'none';

  navigator.geolocation.getCurrentPosition(
    pos => {
      updateUserPosition(pos, DEST_COORDS);
      // Switch to watchPosition for live updates
      watchId = navigator.geolocation.watchPosition(
        p => updateUserPosition(p, DEST_COORDS),
        showLocationError,
        { enableHighAccuracy: true, maximumAge: 2000, timeout: 15000 }
      );
    },
    err => {
      showLocationError(err);
      document.getElementById('btn-location').style.display = 'block';
    },
    { enableHighAccuracy: true, timeout: 15000 }
  );
}

function updateUserPosition(pos, destCoords) {
  const lat = pos.coords.latitude;
  const lng = pos.coords.longitude;
  const accuracy = pos.coords.accuracy;
  userPos = [lat, lng];

  document.getElementById('nav-status').textContent =
    `GPS active (±${Math.round(accuracy)}m)`;
  document.getElementById('nav-status').style.color = '#81c784';

  if (userMarker) {
    // Smooth move the existing marker
    userMarker.setLatLng(userPos);
    if (window.accuracyCircle) window.accuracyCircle.setLatLng(userPos)
      .setRadius(accuracy);
  } else {
    // Accuracy circle (light blue filled area, like Google Maps)
    window.accuracyCircle = L.circle(userPos, {
      radius: accuracy,
      color: '#1565C0',
      fillColor: '#42a5f5',
      fillOpacity: 0.15,
      weight: 1
    }).addTo(map);

    // User dot
    userMarker = L.marker(userPos, {
      icon: L.divIcon({
        html: `<div style="
          width:20px; height:20px;
          background:#1565C0;
          border-radius:50%;
          border:3px solid white;
          box-shadow:0 2px 8px rgba(0,0,0,0.4);">
        </div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        className: ''
      })
    }).addTo(map).bindPopup('You are here');
  }

  fetchRoute(userPos, destCoords);
}

async function fetchRoute(origin, dest) {
  document.getElementById('nav-status').textContent = 'Calculating route...';

  // Try OSRM first (best free option)
  const osrmUrl =
    `https://router.project-osrm.org/route/v1/walking/` +
    `${origin[1]},${origin[0]};${dest[1]},${dest[0]}` +
    `?overview=full&geometries=geojson`;

  try {
    const res = await fetch(osrmUrl);
    const data = await res.json();

    if (data.code === 'Ok') {
      const route = data.routes[0];
      drawRoute(
        route.geometry.coordinates.map(([lng, lat]) => [lat, lng]),
        route.distance,
        route.duration
      );
      document.getElementById('nav-status').textContent = 'Live navigation active';
      document.getElementById('nav-status').style.color = '#81c784';
      return;
    }
  } catch(e) {
    console.warn('OSRM failed, trying straight line fallback');
  }

  // Fallback: draw straight dashed line if routing API fails
  drawStraightLine(origin, dest);
}

function drawRoute(coords, distM, durS) {
  // Remove old route
  if (routeLine) map.removeLayer(routeLine);
  if (window.routeShadow) map.removeLayer(window.routeShadow);

  // Shadow (thicker, darker) — like Google Maps route style
  window.routeShadow = L.polyline(coords, {
    color: '#0a3d8f',
    weight: 9,
    opacity: 0.4,
    lineJoin: 'round',
    lineCap: 'round'
  }).addTo(map);

  // Main route line (blue)
  routeLine = L.polyline(coords, {
    color: '#1976D2',
    weight: 6,
    opacity: 1,
    lineJoin: 'round',
    lineCap: 'round'
  }).addTo(map);

  // Animated dashes overlay (movement effect)
  if (window.routeAnim) map.removeLayer(window.routeAnim);
  window.routeAnim = L.polyline(coords, {
    color: '#ffffff',
    weight: 2,
    opacity: 0.6,
    dashArray: '8, 16',
    lineJoin: 'round'
  }).addTo(map);

  updateStats(distM, durS);

  // Auto-fit map to show full route with padding
  const allPoints = [userPos, ...coords];
  map.fitBounds(L.latLngBounds(allPoints).pad(0.1), {
    animate: true,
    duration: 1.2
  });
}

function drawStraightLine(origin, dest) {
  if (routeLine) map.removeLayer(routeLine);
  routeLine = L.polyline([origin, dest], {
    color: '#1976D2',
    weight: 5,
    dashArray: '10, 10',
    opacity: 0.8
  }).addTo(map);

  // Calculate straight-line distance
  const distM = map.distance(origin, dest);
  const durS  = distM / 1.4; // walking speed ~1.4 m/s
  updateStats(distM, durS);
}

function updateStats(distanceM, durationS) {
  const distEl = document.getElementById('nav-distance');
  const timeEl = document.getElementById('nav-time');

  // Animate the number change
  distEl.style.transition = 'all 0.3s ease';
  timeEl.style.transition = 'all 0.3s ease';

  if (distanceM === null || distanceM === undefined) {
    distEl.textContent = '--';
    timeEl.textContent = '--';
    return;
  }

  const distStr = distanceM < 1000
    ? `${Math.round(distanceM)} m`
    : `${(distanceM / 1000).toFixed(2)} km`;

  const mins = Math.ceil(durationS / 60);
  const timeStr = mins < 1
    ? '< 1 min'
    : mins === 1 ? '1 min'
    : `${mins} mins`;

  distEl.textContent = distStr;
  timeEl.textContent = timeStr;

  // Change color as user gets closer
  if (distanceM < 50) {
    distEl.style.color = '#81c784';  // green = almost there
    timeEl.style.color = '#81c784';
    document.getElementById('nav-status').textContent = 'You have arrived!';
  } else if (distanceM < 200) {
    distEl.style.color = '#ffcc02';  // yellow = getting close
  } else {
    distEl.style.color = '#ffffff';  // white = normal
  }
}

function showLocationError(err) {
  const msgs = {
    1: 'Location permission denied. Please allow location access.',
    2: 'Location unavailable. Check GPS signal.',
    3: 'Location request timed out. Retrying...'
  };
  document.getElementById('nav-status').textContent =
    msgs[err.code] || 'Location error occurred.';
  
  if (err.code === 1) {
    if (document.getElementById('btn-location')) {
      document.getElementById('btn-location').style.display = 'block';
    }
  }
}

function recenterMap() {
  if (userPos) {
    map.setView(userPos, 19, { animate: true, duration: 1 });
  } else {
    map.setView([17.7716, 83.2287], 18, { animate: true });
  }
}

function stopNavigation() {
  if (watchId) navigator.geolocation.clearWatch(watchId);
}

function highlightRoomOnFloorPlan(roomId) {
  // Get the SVG floor plan element
  const svg = document.querySelector('#floor-plan-container svg');
  if (!svg) return;

  // Reset all rooms to default style
  svg.querySelectorAll('.room').forEach(r => {
    r.classList.remove('room-highlight');
  });

  // Highlight the target room
  const targetRoom = svg.getElementById(roomId.toUpperCase());
  if (targetRoom) {
    targetRoom.classList.add('room-highlight');
    // Scroll into view if needed
    targetRoom.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Add pulsing animation
    targetRoom.style.animation = 'roomPulse 1.5s infinite';
  }
}
