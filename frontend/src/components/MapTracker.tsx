import React, { useState, useEffect, useMemo, useRef } from 'react';
import Map, { Marker, Source, Layer, NavigationControl } from 'react-map-gl/maplibre';
import type { ViewStateChangeEvent } from 'react-map-gl/maplibre';
import * as maptilersdk from '@maptiler/sdk';
import '@maptiler/sdk/dist/maptiler-sdk.css';
import { Anchor } from 'lucide-react';

const MAPTILER_KEY = import.meta.env.VITE_MAPTILER_KEY || 'SUcVoJR2d0QVGbessECU';
maptilersdk.config.apiKey = MAPTILER_KEY;

interface MapTrackerProps {
  lat: number;
  lng: number;
  location: string;
}

const MapTracker: React.FC<MapTrackerProps> = ({ lat, lng, location }) => {
  const [viewport, setViewport] = useState({
    latitude: lat,
    longitude: lng,
    zoom: 2.5
  });

  // Keep track of the path traveled
  const [path, setPath] = useState<[number, number][]>([]);
  const prevCoordsRef = useRef<{ lat: number; lng: number } | null>(null);

  useEffect(() => {
    if (!prevCoordsRef.current) {
      // First point: ensure viewport matches
      setViewport(v => ({ ...v, latitude: lat, longitude: lng }));
      setPath([[lng, lat]]);
      prevCoordsRef.current = { lat, lng };
      return;
    }

    const { lat: prevLat, lng: prevLng } = prevCoordsRef.current;
    const dist = Math.sqrt(Math.pow(prevLng - lng, 2) + Math.pow(prevLat - lat, 2));

    if (dist > 10) {
      // Large jump detected: Center camera on new location and reset path
      setViewport(v => ({ ...v, latitude: lat, longitude: lng, zoom: 2.5 }));
      setPath([[lng, lat]]);
    } else if (dist > 0.0001) {
      setPath(prev => [...prev, [lng, lat] as [number, number]].slice(-500));
    }
    
    prevCoordsRef.current = { lat, lng };
  }, [lat, lng]);

  const geojson: any = useMemo(() => {
    const features = [];
    if (path.length > 0) {
      let currentSegment: [number, number][] = [path[0]];
      
      for (let i = 1; i < path.length; i++) {
        const prev = path[i - 1];
        const curr = path[i];
        
        // If we cross the IDL (jump > 180 degrees)
        if (Math.abs(curr[0] - prev[0]) > 180) {
          features.push({
            type: "Feature",
            properties: {},
            geometry: {
              type: "LineString",
              coordinates: currentSegment,
            },
          });
          currentSegment = [];
        }
        currentSegment.push(curr);
      }
      
      if (currentSegment.length > 0) {
        features.push({
          type: "Feature",
          properties: {},
          geometry: {
            type: "LineString",
            coordinates: currentSegment,
          },
        });
      }
    }
    
    return {
      type: "FeatureCollection",
      features: features
    };
  }, [path]);

  return (
    <div className="glass-card overflow-hidden h-[400px] relative bg-slate-800">
      <Map
        {...viewport}
        onMove={(evt: ViewStateChangeEvent) => setViewport(evt.viewState)}
        mapLib={maptilersdk as any}
        mapStyle={`https://api.maptiler.com/maps/basic-v2-dark/style.json?key=${MAPTILER_KEY}`}
        projection={{ name: 'globe' } as any}
      >
        <NavigationControl position="top-right" />
        
        {/* Traveled Path Layer */}
        <Source id="my-data" type="geojson" data={geojson}>
          <Layer
            id="line-layer"
            type="line"
            layout={{ 'line-join': 'round', 'line-cap': 'round' }}
            paint={{ 'line-color': '#6366f1', 'line-width': 3, 'line-opacity': 0.6 }}
          />
        </Source>

        <Marker latitude={lat} longitude={lng} anchor="bottom">
          <div className="relative">
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] font-bold py-1 px-2 rounded whitespace-nowrap shadow-xl border border-slate-700">
              {location}
            </div>
            <div className="bg-brand-primary p-2 rounded-full shadow-lg shadow-indigo-500/50 border-2 border-white animate-bounce">
              <Anchor className="text-white" size={16} />
            </div>
          </div>
        </Marker>
      </Map>
      
      {MAPTILER_KEY.includes('REPLACE') && (
        <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center p-8 text-center backdrop-blur-sm">
          <div className="max-w-xs">
            <h4 className="text-white font-bold mb-2">MapTiler Key Required</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              To see the live satellite tracking, please provide a valid MapTiler API key in <code>MapTracker.tsx</code>.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapTracker;
