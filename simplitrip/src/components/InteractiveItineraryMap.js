import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { resolveCoordinates } from '../utils/geocoding';

// Fix traditional Leaflet icon issue in Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const MapBoundsUpdater = ({ coordinates }) => {
    const map = useMap();
    useEffect(() => {
        if (coordinates && coordinates.length > 0) {
            const bounds = L.latLngBounds(coordinates);
            map.fitBounds(bounds, { padding: [50, 50], animate: true, duration: 1 });
        }
    }, [coordinates, map]);
    return null;
};

const InteractiveItineraryMap = ({ destination, origin }) => {
    const [route, setRoute] = useState([]);
    const [loading, setLoading] = useState(true);
    const [distanceKm, setDistanceKm] = useState(null);
    const [osrmPolyline, setOsrmPolyline] = useState(null);

    useEffect(() => {
        const fetchRoute = async () => {
            setLoading(true);
            try {
                const points = [];
                let originCoords = null;
                let destCoords = null;

                if (origin) {
                    originCoords = await resolveCoordinates(origin);
                    if (originCoords) points.push({ name: origin, lat: originCoords.lat, lon: originCoords.lon });
                }
                if (destination) {
                    destCoords = await resolveCoordinates(destination);
                    if (destCoords) points.push({ name: destination, lat: destCoords.lat, lon: destCoords.lon });
                }
                setRoute(points);

                if (originCoords && destCoords) {
                    try {
                        const osrmRes = await fetch(`https://router.project-osrm.org/route/v1/driving/${originCoords.lon},${originCoords.lat};${destCoords.lon},${destCoords.lat}?overview=full&geometries=geojson`);
                        if (osrmRes.ok) {
                            const osrmData = await osrmRes.json();
                            if (osrmData.routes && osrmData.routes.length > 0) {
                                const bestRoute = osrmData.routes[0];
                                setDistanceKm((bestRoute.distance / 1000).toFixed(1));
                                const osrmPath = bestRoute.geometry.coordinates.map(c => [c[1], c[0]]);
                                setOsrmPolyline(osrmPath);
                            }
                        }
                    } catch (routeErr) {
                        console.error("OSRM Routing failed", routeErr);
                    }
                }
            } catch (err) {
                console.error("Geocoding failed", err);
            }
            setLoading(false);
        };

        fetchRoute();
    }, [destination, origin]);

    if (loading) {
        return (
            <div className="h-full w-full flex items-center justify-center bg-gray-800">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 font-bold border-4 border-t-cyan-500 border-gray-600 rounded-full animate-spin"></div>
                    <p className="text-gray-400 font-semibold text-sm animate-pulse">Engaging Global Satellite Maps...</p>
                </div>
            </div>
        );
    }

    // Default to center of India if nowhere is supplied
    const mapCenter = route.length > 0 ? [route[0].lat, route[0].lon] : [20.5937, 78.9629];

    return (
        <div className="h-full w-full relative z-0">
            <MapContainer center={mapCenter} zoom={4} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {route.map((point, i) => (
                    <Marker key={i} position={[point.lat, point.lon]}>
                        <Popup className="font-bold text-gray-800">{point.name}</Popup>
                    </Marker>
                ))}
                {osrmPolyline ? (
                    <Polyline positions={osrmPolyline} color="#06b6d4" weight={5} />
                ) : (
                    route.length > 1 && (
                        <Polyline positions={route.map(p => [p.lat, p.lon])} color="#06b6d4" weight={5} dashArray="10, 10" />
                    )
                )}
                <MapBoundsUpdater coordinates={osrmPolyline || route.map(p => [p.lat, p.lon])} />
            </MapContainer>

            {distanceKm && (
                <div className="absolute top-4 right-4 z-[400] bg-gray-900/80 backdrop-blur-md border border-cyan-500/50 px-4 py-2 rounded-xl shadow-lg shadow-cyan-500/20">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider block mb-1">Driving Distance</span>
                    <span className="text-cyan-400 font-bold text-xl">{distanceKm} <span className="text-sm">km</span></span>
                </div>
            )}
        </div>
    );
};

export default InteractiveItineraryMap;
