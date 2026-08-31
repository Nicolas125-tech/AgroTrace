'use client';
import { useMemo } from 'react';
import Map, { Source, Layer } from 'react-map-gl';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface RouteMapProps {
  route: { lat: number; lng: number }[];
}

export function RouteMap({ route }: RouteMapProps) {
  const geojson = useMemo(() => {
    if (!route || route.length === 0) return null;
    return {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: route.map(point => [point.lng, point.lat]),
          },
          properties: {},
        }
      ]
    };
  }, [route]);

  if (!route || route.length === 0) return <div className="p-4 text-center">No route data available</div>;

  return (
    <div className="h-[400px] w-full rounded-lg overflow-hidden border">
      <Map
        mapLib={maplibregl}
        initialViewState={{
          longitude: route[0].lng,
          latitude: route[0].lat,
          zoom: 12
        }}
        mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
      >
        {geojson && (
          <Source id="route-source" type="geojson" data={geojson as any}>
            <Layer
              id="route-layer"
              type="line"
              source="route-source"
              layout={{ 'line-join': 'round', 'line-cap': 'round' }}
              paint={{ 'line-color': '#3b82f6', 'line-width': 4 }}
            />
          </Source>
        )}
      </Map>
    </div>
  );
}
