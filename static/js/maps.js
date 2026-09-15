/**
 * DLDMS worker map — real Leaflet.js + OpenStreetMap tiles.
 * Replaces the earlier hand-drawn SVG placeholder with an actual interactive,
 * zoomable/pannable map, per the original tech-stack requirement.
 */
(function () {
  "use strict";

  const ZAMBIA_CENTER = [-13.5, 27.85];
  const ZAMBIA_DEFAULT_ZOOM = 6;

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function markerPopupHtml(marker) {
    return (
      '<div class="map-popup">' +
      "<strong>" + escapeHtml(marker.name) + "</strong><br>" +
      '<span class="text-xs text-slate-500">' + escapeHtml(marker.unique_id) + "</span><br>" +
      '<span class="text-xs">' + escapeHtml(marker.district) + ", " + escapeHtml(marker.province) + "</span><br>" +
      '<span class="text-xs text-slate-500">' + escapeHtml(marker.capture_source) + " &middot; " + escapeHtml(marker.capture_mode) + "</span><br>" +
      '<a class="text-xs font-semibold text-teal-700" href="' + marker.url + '">View worker &rarr;</a>' +
      "</div>"
    );
  }

  function renderLocalMap(elementId, markers, options) {
    const opts = options || {};
    const container = document.getElementById(elementId);
    if (!container) return null;

    if (typeof L === "undefined") {
      container.innerHTML = '<p class="p-4 text-sm text-slate-500">Map library failed to load. Check your internet connection.</p>';
      return null;
    }

    const validMarkers = (markers || []).filter(function (m) {
      return typeof m.lat === "number" && typeof m.lng === "number";
    });

    const map = L.map(container, { scrollWheelZoom: true }).setView(ZAMBIA_CENTER, ZAMBIA_DEFAULT_ZOOM);

    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
      attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
      maxZoom: 16,
    }).addTo(map);

    if (validMarkers.length === 0) {
      const emptyControl = L.control({ position: "topright" });
      emptyControl.onAdd = function () {
        const div = L.DomUtil.create("div", "map-empty-banner");
        div.textContent = opts.emptyMessage || "No mapped records yet.";
        return div;
      };
      emptyControl.addTo(map);
      return map;
    }

    const markerGroup = L.featureGroup();
    validMarkers.forEach(function (marker) {
      const leafletMarker = L.marker([marker.lat, marker.lng]);
      leafletMarker.bindPopup(markerPopupHtml(marker));
      leafletMarker.addTo(markerGroup);
    });
    markerGroup.addTo(map);

    try {
      map.fitBounds(markerGroup.getBounds().pad(0.2), { maxZoom: 12 });
    } catch (err) {
      // getBounds() can throw on a single point with no spread; the default view is fine.
    }

    return map;
  }

  window.DLDMSMaps = { renderLocalMap: renderLocalMap };
})();
