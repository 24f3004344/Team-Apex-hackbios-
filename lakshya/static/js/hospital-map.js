/**
 * AarogyaSahay Healthcare Grid - Interactive Hospital Map Engine
 * Powered by Leaflet & OpenStreetMap (Reliable, Zero-Key Dependency, Offline-Resilient)
 */

(function(window) {
    'use strict';

    // Global map instances & registries
    let listMap = null;
    let detailMap = null;
    let markersLayer = null;
    let hospitalMarkersById = {};
    let allHospitalsData = [];
    let userMarker = null;

    // SVG Marker pin generators for Public & Private facilities
    function createMarkerIcon(hospitalType, isPrimary = false) {
        const isPublic = (hospitalType || '').toLowerCase() === 'public';
        const mainColor = isPublic ? '#059669' : '#2563eb';
        const shadowColor = isPublic ? 'rgba(5, 150, 105, 0.35)' : 'rgba(37, 99, 235, 0.35)';
        const size = isPrimary ? 38 : 32;

        const svgHtml = `
            <div class="custom-hospital-marker ${isPrimary ? 'primary-pin' : ''}" style="
                width: ${size}px;
                height: ${size}px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: ${mainColor};
                color: #ffffff;
                border: 2.5px solid #ffffff;
                border-radius: 50% 50% 50% 4px;
                transform: rotate(-45deg);
                box-shadow: 0 4px 10px ${shadowColor};
                cursor: pointer;
                transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
            ">
                <svg viewBox="0 0 24 24" width="${isPrimary ? 18 : 15}" height="${isPrimary ? 18 : 15}" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="transform: rotate(45deg);">
                    <path d="M12 6v12M6 12h12"/>
                </svg>
            </div>
        `;

        return L.divIcon({
            html: svgHtml,
            className: 'hospital-marker-container',
            iconSize: [size, size],
            iconAnchor: [size / 2, size],
            popupAnchor: [0, -size]
        });
    }

    function createPopupHtml(hospital) {
        const isPublic = (hospital.hospital_type || '').toLowerCase() === 'public';
        const typeBadge = isPublic
            ? '<span class="type-badge type-public" style="background:#dcfce7; color:#166534; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px;">Public Health Centre</span>'
            : '<span class="type-badge type-private" style="background:#e0f2fe; color:#0369a1; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px;">Private Hospital</span>';

        const phoneHtml = hospital.phone1
            ? `<div style="margin-top:6px; font-size:12px;"><a href="tel:${escapeHtml(hospital.phone1)}" style="color:#2563eb; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">📞 <strong>${escapeHtml(hospital.phone1)}</strong></a></div>`
            : '';

        const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`;

        return `
            <div class="map-popup-card" style="font-family:'Plus Jakarta Sans',sans-serif; min-width:240px; max-width:280px; padding:4px 0;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px; margin-bottom:6px;">
                    <h4 style="margin:0; font-size:14px; font-weight:700; color:#0f172a; line-height:1.3;">${escapeHtml(hospital.hospital_name)}</h4>
                </div>
                <div style="margin-bottom:8px;">${typeBadge}</div>
                <div style="font-size:11.5px; color:#64748b; line-height:1.4; margin-bottom:8px;">
                    <strong style="color:#334155;">${escapeHtml(hospital.district)} District</strong><br>
                    ${escapeHtml((hospital.address || '').substring(0, 95))}${hospital.address && hospital.address.length > 95 ? '...' : ''}
                </div>
                ${phoneHtml}
                <div style="display:flex; gap:6px; margin-top:10px; border-top:1px solid #f1f5f9; padding-top:8px;">
                    <a href="/hospitals/${hospital.id}" class="btn btn-primary btn-sm" style="flex:1; text-align:center; padding:6px 10px; font-size:11.5px; font-weight:600; text-decoration:none; border-radius:6px; background:#2563eb; color:#ffffff;">Facility Details</a>
                    <a href="${directionsUrl}" target="_blank" rel="noopener" class="btn btn-outline btn-sm" style="flex:1; text-align:center; padding:6px 10px; font-size:11.5px; font-weight:600; text-decoration:none; border-radius:6px; border:1px solid #cbd5e1; color:#334155; background:#f8fafc;">Directions ↗</a>
                </div>
            </div>
        `;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    /**
     * Initialize interactive hospital list map
     */
    function initHospitalListMap(containerId, hospitals, selectedDistrict) {
        const container = document.getElementById(containerId);
        if (!container || typeof L === 'undefined') return null;

        // Clean up previous map instance if any
        if (listMap) {
            listMap.remove();
            listMap = null;
        }

        allHospitalsData = hospitals || [];
        hospitalMarkersById = {};

        // Default center: Chhattisgarh Center (Raipur / Bilaspur region)
        const defaultCenter = [21.2514, 81.6296];
        const defaultZoom = selectedDistrict ? 11 : 7;

        listMap = L.map(containerId, {
            center: defaultCenter,
            zoom: defaultZoom,
            zoomControl: false,
            scrollWheelZoom: true
        });

        // Add top-right zoom control
        L.control.zoom({ position: 'topright' }).addTo(listMap);

        // High quality OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(listMap);

        // Marker layer group
        markersLayer = L.featureGroup().addTo(listMap);

        renderMarkers(allHospitalsData);

        window.hospitalMap = listMap;
        return listMap;
    }

    function renderMarkers(hospitalsToRender) {
        if (!markersLayer || !listMap) return;
        markersLayer.clearLayers();
        hospitalMarkersById = {};

        const validHospitals = (hospitalsToRender || []).filter(h => h.latitude && h.longitude);

        validHospitals.forEach(hospital => {
            const lat = parseFloat(hospital.latitude);
            const lng = parseFloat(hospital.longitude);
            if (isNaN(lat) || isNaN(lng)) return;

            const icon = createMarkerIcon(hospital.hospital_type);
            const marker = L.marker([lat, lng], {
                icon: icon,
                title: hospital.hospital_name,
                riseOnHover: true
            });

            marker.bindPopup(createPopupHtml(hospital), {
                maxWidth: 300,
                className: 'clinical-map-popup'
            });

            marker.on('click', function() {
                marker.openPopup();
            });

            markersLayer.addLayer(marker);
            hospitalMarkersById[hospital.id] = marker;
        });

        // Fit bounds if markers exist
        if (validHospitals.length > 0) {
            try {
                listMap.fitBounds(markersLayer.getBounds().pad(0.12), {
                    maxZoom: 14,
                    animate: true
                });
            } catch (e) {
                console.warn('Could not fit map bounds:', e);
            }
        }
    }

    /**
     * Focus and highlight a single hospital when clicked in list/table
     */
    function focusHospital(hospitalId) {
        const marker = hospitalMarkersById[hospitalId];
        const container = document.getElementById('hospital-map') || document.getElementById('map-section');

        if (container) {
            container.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        if (marker && listMap) {
            setTimeout(() => {
                listMap.setView(marker.getLatLng(), 15, { animate: true });
                marker.openPopup();
            }, 300);
        }
    }

    /**
     * Filter map markers by type ('All', 'Public', 'Private')
     */
    function filterMapByType(type) {
        if (!allHospitalsData || allHospitalsData.length === 0) return;

        if (!type || type.toLowerCase() === 'all') {
            renderMarkers(allHospitalsData);
        } else {
            const filtered = allHospitalsData.filter(h => (h.hospital_type || '').toLowerCase() === type.toLowerCase());
            renderMarkers(filtered);
        }

        const btn = document.getElementById('toggleMapBtn');
        if (btn) {
            btn.innerText = type === 'Public' ? 'Show Private' : (type === 'Private' ? 'Show All' : 'Show Public');
        }
    }

    /**
     * Locate user with HTML5 Geolocation API
     */
    function locateUser() {
        if (!navigator.geolocation) {
            if (window.showToast) window.showToast("Geolocation is not supported by your browser.", "warning");
            return;
        }

        if (window.showToast) window.showToast("Detecting your location in Chhattisgarh...", "info");

        navigator.geolocation.getCurrentPosition(
            position => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                if (listMap) {
                    if (userMarker) {
                        listMap.removeLayer(userMarker);
                    }

                    const userIcon = L.divIcon({
                        html: `<div style="width:20px; height:20px; background:#2563eb; border:3px solid #ffffff; border-radius:50%; box-shadow:0 0 0 6px rgba(37,99,235,0.3); animation:pulse 2s infinite;"></div>`,
                        className: 'user-location-marker',
                        iconSize: [20, 20],
                        iconAnchor: [10, 10]
                    });

                    userMarker = L.marker([lat, lng], { icon: userIcon }).addTo(listMap);
                    userMarker.bindPopup("<strong>Your Current Location</strong>").openPopup();
                    listMap.setView([lat, lng], 13, { animate: true });

                    if (window.showToast) window.showToast("Location detected. Showing nearest healthcare facilities.", "success");
                }
            },
            err => {
                if (window.showToast) window.showToast("Could not determine your location. Please check browser permissions.", "warning");
            },
            { enableHighAccuracy: true, timeout: 8000 }
        );
    }

    /**
     * Initialize hospital detail page map
     */
    function initHospitalDetailMap(containerId, mainHospital, nearbyHospitals = []) {
        const container = document.getElementById(containerId);
        if (!container || typeof L === 'undefined') return null;

        if (detailMap) {
            detailMap.remove();
            detailMap = null;
        }

        const lat = parseFloat(mainHospital.latitude);
        const lng = parseFloat(mainHospital.longitude);

        if (isNaN(lat) || isNaN(lng)) {
            container.innerHTML = `
                <div style="display:flex; align-items:center; justify-content:center; height:100%; color:#64748b; text-align:center; padding:2rem; background:#f8fafc; border-radius:8px;">
                    <div>
                        <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:8px; color:#94a3b8;">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        <p style="margin:0; font-weight:600;">Geocoordinates pending for this facility.</p>
                    </div>
                </div>
            `;
            return null;
        }

        detailMap = L.map(containerId, {
            center: [lat, lng],
            zoom: 15,
            zoomControl: true,
            scrollWheelZoom: false
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(detailMap);

        const group = L.featureGroup().addTo(detailMap);

        // Add main hospital marker
        const mainIcon = createMarkerIcon(mainHospital.hospital_type, true);
        const mainMarker = L.marker([lat, lng], {
            icon: mainIcon,
            title: mainHospital.hospital_name,
            zIndexOffset: 1000
        }).addTo(group);

        mainMarker.bindPopup(createPopupHtml(mainHospital), {
            maxWidth: 320,
            className: 'clinical-map-popup'
        }).openPopup();

        // Add nearby secondary hospitals
        (nearbyHospitals || []).forEach(h => {
            if (h.id === mainHospital.id) return;
            const nLat = parseFloat(h.latitude);
            const nLng = parseFloat(h.longitude);
            if (isNaN(nLat) || isNaN(nLng)) return;

            const nIcon = createMarkerIcon(h.hospital_type, false);
            const nMarker = L.marker([nLat, nLng], {
                icon: nIcon,
                title: h.hospital_name
            }).addTo(group);

            nMarker.bindPopup(createPopupHtml(h), { maxWidth: 300 });
        });

        return detailMap;
    }

    // Export to global scope
    window.initHospitalListMap = initHospitalListMap;
    window.initHospitalDetailMap = initHospitalDetailMap;
    window.focusHospital = focusHospital;
    window.filterMapByType = filterMapByType;
    window.locateUser = locateUser;

    // Backward compatibility bridges
    window.initMap = function() {
        console.log("AarogyaSahay Map Engine active.");
    };
    window.showHospitalMapDetail = function(hospitalId) {
        focusHospital(hospitalId);
    };

})(window);