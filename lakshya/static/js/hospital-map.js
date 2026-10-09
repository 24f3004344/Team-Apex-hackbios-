/**
 * Google Maps Integration for Hospital Directory
 * Handles map initialization, markers, and info windows
 */

let map = null;
let markers = [];
let infoWindow = null;
let userLocation = null;

// Initialize map when Google Maps API loads
window.initMap = function() {
    // Default center: Raipur, Chhattisgarh
    const defaultCenter = { lat: 21.2514, lng: 81.6296 };
    
    map = new google.maps.Map(document.getElementById('hospital-map'), {
        center: defaultCenter,
        zoom: 10,
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true,
        styles: [
            {
                featureType: 'poi.medical',
                elementType: 'labels',
                stylers: [{ visibility: 'on' }]
            }
        ]
    });
    
    infoWindow = new google.maps.InfoWindow();
    
    // Try to get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                // Add user location marker
                addUserLocationMarker(userLocation);
                // Center map on user if no hospitals loaded yet
                if (markers.length === 0) {
                    map.setCenter(userLocation);
                    map.setZoom(13);
                }
            },
            (error) => {
                console.log('Geolocation not available:', error.message);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
        );
    }
    
    // Make map globally accessible
    window.hospitalMap = map;
};

// Add user location marker
function addUserLocationMarker(location) {
    if (!map) return;
    
    const marker = new google.maps.Marker({
        position: location,
        map: map,
        title: 'Your Location',
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#4285F4',
            fillOpacity: 1,
            strokeColor: '#FFFFFF',
            strokeWeight: 2
        },
        zIndex: 1000
    });
    
    marker.addListener('click', () => {
        infoWindow.setContent('<div style="padding: 8px;"><strong>Your Location</strong></div>');
        infoWindow.open(map, marker);
    });
}

// Add hospital markers to map
function addHospitalMarkers(hospitals) {
    if (!map) return;
    
    // Clear existing markers
    clearMarkers();
    
    const bounds = new google.maps.LatLngBounds();
    let hasValidCoords = false;
    
    hospitals.forEach(hospital => {
        if (hospital.latitude && hospital.longitude) {
            const position = { lat: hospital.latitude, lng: hospital.longitude };
            
            // Choose icon based on hospital type
            const isPublic = hospital.hospital_type === 'Public';
            const icon = {
                url: isPublic 
                    ? 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" fill="#10B981" stroke="#FFFFFF" stroke-width="2"/>
                            <path d="M12 8v4M12 16h.01" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    `)
                    : 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" fill="#3B82F6" stroke="#FFFFFF" stroke-width="2"/>
                            <path d="M12 8v4M12 16h.01" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    `),
                scaledSize: new google.maps.Size(32, 32),
                anchor: new google.maps.Point(16, 16)
            };
            
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: hospital.hospital_name,
                icon: icon,
                hospitalId: hospital.id
            });
            
            // Create info window content
            const content = createInfoWindowContent(hospital);
            
            marker.addListener('click', () => {
                infoWindow.setContent(content);
                infoWindow.open(map, marker);
            });
            
            markers.push(marker);
            bounds.extend(position);
            hasValidCoords = true;
        }
    });
    
    // Fit map to show all markers
    if (hasValidCoords && markers.length > 0) {
        map.fitBounds(bounds);
        // Don't zoom in too much if only one marker
        if (markers.length === 1) {
            map.setZoom(15);
        }
    }
    
    return markers.length;
}

// Create info window content for hospital
function createInfoWindowContent(hospital) {
    const typeClass = hospital.hospital_type === 'Public' ? 'public' : 'private';
    const typeLabel = hospital.hospital_type === 'Public' ? '🏥 Public' : '🏥 Private';
    
    return `
        <div class="map-info-window" style="min-width: 250px; max-width: 300px; padding: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                <h4 style="margin: 0; font-size: 14px; font-weight: 600; color: #1f2937;">${escapeHtml(hospital.hospital_name)}</h4>
                <span class="type-badge type-${typeClass}" style="font-size: 10px; padding: 2px 6px; border-radius: 10px; background: ${typeClass === 'public' ? '#DCFCE7' : '#E0F2FE'}; color: ${typeClass === 'public' ? '#166534' : '#075985'};">${typeLabel}</span>
            </div>
            <div style="font-size: 12px; color: #4b5563; margin-bottom: 8px;">
                <div>${escapeHtml(hospital.district)} District, Chhattisgarh</div>
                ${hospital.address ? `<div style="margin-top: 4px;">${escapeHtml(hospital.address.substring(0, 100))}${hospital.address.length > 100 ? '...' : ''}</div>` : ''}
            </div>
            <div style="font-size: 12px; color: #4b5563; margin-bottom: 8px;">
                ${hospital.phone1 ? `<div>📞 <a href="tel:${escapeHtml(hospital.phone1)}" style="color: #2563eb; text-decoration: none;">${escapeHtml(hospital.phone1)}</a></div>` : ''}
                ${hospital.phone2 ? `<div>📞 <a href="tel:${escapeHtml(hospital.phone2)}" style="color: #2563eb; text-decoration: none;">${escapeHtml(hospital.phone2)}</a></div>` : ''}
                ${hospital.email ? `<div>✉️ <a href="mailto:${escapeHtml(hospital.email)}" style="color: #2563eb; text-decoration: none;">${escapeHtml(hospital.email)}</a></div>` : ''}
            </div>
            <div style="display: flex; gap: 8px;">
                <a href="/hospitals/${hospital.id}" class="btn btn-primary btn-sm" style="padding: 6px 12px; font-size: 12px; text-decoration: none; background: #2563eb; color: white; border-radius: 4px;">View Details</a>
                ${hospital.latitude && hospital.longitude ? `<a href="https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}" target="_blank" class="btn btn-outline btn-sm" style="padding: 6px 12px; font-size: 12px; text-decoration: none; border: 1px solid #d1d5db; color: #374151; border-radius: 4px;">Directions</a>` : ''}
            </div>
        </div>
    `;
}

// Clear all markers
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

// Show single hospital on map (for detail page)
function showHospitalOnMap(hospital) {
    if (!map || !hospital.latitude || !hospital.longitude) return;
    
    const position = { lat: hospital.latitude, lng: hospital.longitude };
    
    // Clear existing markers
    clearMarkers();
    
    // Add hospital marker
    const isPublic = hospital.hospital_type === 'Public';
    const icon = {
        url: isPublic 
            ? 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" fill="#10B981" stroke="#FFFFFF" stroke-width="3"/>
                    <path d="M12 8v4M12 16h.01" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
                </svg>
            `)
            : 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" fill="#3B82F6" stroke="#FFFFFF" stroke-width="3"/>
                    <path d="M12 8v4M12 16h.01" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
                </svg>
            `),
        scaledSize: new google.maps.Size(40, 40),
        anchor: new google.maps.Point(20, 20)
    };
    
    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: hospital.hospital_name,
        icon: icon,
        animation: google.maps.Animation.DROP
    });
    
    markers.push(marker);
    
    // Center map on hospital
    map.setCenter(position);
    map.setZoom(16);
    
    // Open info window
    const content = createInfoWindowContent(hospital);
    infoWindow.setContent(content);
    infoWindow.open(map, marker);
    
    // Add user location if available
    if (userLocation) {
        addUserLocationMarker(userLocation);
    }
}

// Get directions to hospital
function getDirections(hospital) {
    if (!hospital.latitude || !hospital.longitude) {
        alert('Location not available for this hospital');
        return;
    }
    
    const url = `https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`;
    window.open(url, '_blank');
}

// Find nearby hospitals (using Places API or simple radius search)
function findNearbyHospitals(location, radius = 5000) {
    if (!map) return Promise.resolve([]);
    
    return new Promise((resolve) => {
        const service = new google.maps.places.PlacesService(map);
        const request = {
            location: location,
            radius: radius,
            type: ['hospital'],
            keyword: 'hospital'
        };
        
        service.nearbySearch(request, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                resolve(results.map(place => ({
                    name: place.name,
                    latitude: place.geometry.location.lat(),
                    longitude: place.geometry.location.lng(),
                    address: place.vicinity,
                    placeId: place.place_id
                })));
            } else {
                resolve([]);
            }
        });
    });
}

// Utility function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize map on a specific container (for detail page)
function initMapOnContainer(containerId, center, zoom = 15) {
    if (typeof google === 'undefined' || !google.maps) {
        console.warn('Google Maps API not loaded yet');
        return null;
    }
    
    const container = document.getElementById(containerId);
    if (!container) return null;
    
    const mapInstance = new google.maps.Map(container, {
        center: center,
        zoom: zoom,
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true
    });
    
    return mapInstance;
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initMap,
        addHospitalMarkers,
        showHospitalOnMap,
        getDirections,
        findNearbyHospitals,
        clearMarkers
    };
}