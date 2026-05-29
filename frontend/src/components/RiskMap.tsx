import React from "react";
import Map, { Marker, Source, Layer, NavigationControl } from "react-map-gl/maplibre";
import type { ViewStateChangeEvent } from "react-map-gl/maplibre";
import * as maptilersdk from "@maptiler/sdk";
import "@maptiler/sdk/dist/maptiler-sdk.css";
import "maplibre-gl/dist/maplibre-gl.css";
import { Anchor, AlertCircle } from "lucide-react";

// MapTiler Configuration
const MAPTILER_KEY = import.meta.env.VITE_MAPTILER_KEY || 'SUcVoJR2d0QVGbessECU';
maptilersdk.config.apiKey = MAPTILER_KEY;

interface RiskMapProps {
  waypoints: { lat: number; lng: number }[];
  riskLevel: "Low" | "Medium" | "High";
}

const RiskMap: React.FC<RiskMapProps> = ({ waypoints, riskLevel }) => {
  const [viewport, setViewport] = React.useState({
    latitude: 35,
    longitude: 170,
    zoom: 1.5,
  });

  const geojson: any = React.useMemo(() => {
    const features = [];
    if (waypoints.length > 0) {
      let currentSegment: [number, number][] = [[waypoints[0].lng, waypoints[0].lat]];
      
      for (let i = 1; i < waypoints.length; i++) {
        const prev = waypoints[i - 1];
        const curr = waypoints[i];
        
        // If we cross the IDL (jump > 180 degrees)
        if (Math.abs(curr.lng - prev.lng) > 180) {
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
        currentSegment.push([curr.lng, curr.lat]);
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
  }, [waypoints]);

  const getRiskColor = () => {
    switch (riskLevel) {
      case "High":
        return "#be123c";
      case "Medium":
        return "#d97706";
      default:
        return "#059669";
    }
  };

  return (
    <div className="glass-card overflow-hidden h-[500px] relative bg-slate-800">
      <Map
        {...viewport}
        onMove={(evt: ViewStateChangeEvent) => setViewport(evt.viewState)}
        mapLib={maptilersdk as any}
        mapStyle={`https://api.maptiler.com/maps/streets-v2-dark/style.json?key=${MAPTILER_KEY}`}
        renderWorldCopies={false}
        projection={"globe" as any}
      >
        <NavigationControl position="top-right" />

        <Source id="route-data" type="geojson" data={geojson}>
          <Layer
            id="route-line"
            type="line"
            layout={{ "line-join": "round", "line-cap": "round" }}
            paint={{
              "line-color": getRiskColor(),
              "line-width": 4,
              "line-dasharray": [2, 1],
            }}
          />
        </Source>

        {waypoints.length > 0 && (
          <>
            <Marker
              latitude={waypoints[0].lat}
              longitude={waypoints[0].lng}
              anchor="bottom"
            >
              <div className="bg-slate-900 p-1 rounded-full border-2 border-white shadow-lg">
                <Anchor className="text-white" size={12} />
              </div>
            </Marker>
            <Marker
              latitude={waypoints[waypoints.length - 1].lat}
              longitude={waypoints[waypoints.length - 1].lng}
              anchor="bottom"
            >
              <div className="bg-brand-primary p-1 rounded-full border-2 border-white shadow-lg">
                <div className="w-2 h-2 bg-white rounded-full" />
              </div>
            </Marker>
          </>
        )}
      </Map>

      <div className="absolute bottom-6 left-6 flex items-center space-x-3 bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-slate-200/50 shadow-xl">
        <div
          className={`p-2 rounded-xl ${riskLevel === "High" ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"}`}
        >
          <AlertCircle size={20} />
        </div>
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase">
            Route Risk Level
          </p>
          <p
            className={`text-sm font-black ${riskLevel === "High" ? "text-rose-700" : "text-emerald-700"}`}
          >
            {riskLevel} Alert
          </p>
        </div>
      </div>

      {MAPTILER_KEY.includes("REPLACE") && (
        <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center p-8 text-center backdrop-blur-sm z-50">
          <div className="max-w-xs">
            <h4 className="text-white font-bold mb-2">MapTiler Key Required</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              To visualize the maritime route, please provide a valid MapTiler
              API key in <code>RiskMap.tsx</code>.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskMap;
