import React, { useState, useEffect } from 'react';
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre';
import * as maptilersdk from '@maptiler/sdk';
import { api } from '../services/api';
import { Ship, AlertTriangle, DollarSign, Layers, Activity } from 'lucide-react';

const MAPTILER_KEY = 'SUcVoJR2d0QVGbessECU';
maptilersdk.config.apiKey = MAPTILER_KEY;

const FleetView: React.FC = () => {
  const [fleet, setFleet] = useState<any[]>([]);

  useEffect(() => {
    const fetchFleet = async () => {
      try {
        const data = await api.getFleet();
        setFleet(data);
      } catch (error) {
        console.error("Failed to fetch fleet:", error);
      }
    };

    fetchFleet();
    const interval = setInterval(fetchFleet, 5000);
    return () => clearInterval(interval);
  }, []);

  const stats = {
    totalVessels: fleet.length,
    atRisk: fleet.filter(v => v.status !== 'Normal').length,
    totalValue: fleet.reduce((acc, v) => acc + v.cargo_value, 0).toFixed(1),
    totalTEU: fleet.reduce((acc, v) => acc + v.teu_count, 0).toLocaleString()
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Fleet Command Center</h1>
        <p className="text-slate-500 mt-1">Real-time global oversight and predictive risk monitoring.</p>
      </header>

      {/* Fleet Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 flex items-center space-x-4">
          <div className="bg-blue-50 p-3 rounded-2xl text-blue-600">
            <Ship size={24} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active Vessels</p>
            <p className="text-2xl font-black text-slate-900">{stats.totalVessels}</p>
          </div>
        </div>
        <div className="glass-card p-6 flex items-center space-x-4">
          <div className="bg-rose-50 p-3 rounded-2xl text-rose-600">
            <AlertTriangle size={24} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Vessels at Risk</p>
            <p className="text-2xl font-black text-slate-900">{stats.atRisk}</p>
          </div>
        </div>
        <div className="glass-card p-6 flex items-center space-x-4">
          <div className="bg-emerald-50 p-3 rounded-2xl text-emerald-600">
            <DollarSign size={24} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Cargo Value (USD)</p>
            <p className="text-2xl font-black text-slate-900">${stats.totalValue}M</p>
          </div>
        </div>
        <div className="glass-card p-6 flex items-center space-x-4">
          <div className="bg-indigo-50 p-3 rounded-2xl text-indigo-600">
            <Layers size={24} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Fleet Load</p>
            <p className="text-2xl font-black text-slate-900">{stats.totalTEU} TEU</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Global Map */}
        <div className="lg:col-span-2 glass-card overflow-hidden h-[500px] relative bg-slate-800">
          <Map
            initialViewState={{
              latitude: 20,
              longitude: 0,
              zoom: 1.5
            }}
            mapLib={maptilersdk as any}
            mapStyle={`https://api.maptiler.com/maps/basic-v2-dark/style.json?key=${MAPTILER_KEY}`}
            renderWorldCopies={false}
          >
            <NavigationControl position="top-right" />
            
            {fleet.map((v) => (
              <Marker key={v.id} latitude={v.lat} longitude={v.lng} anchor="bottom">
                <div className="group relative cursor-pointer">
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                    <div className="bg-slate-900 text-white p-3 rounded-xl shadow-2xl border border-white/10 w-48">
                      <p className="text-[10px] font-bold text-indigo-400 uppercase mb-1">{v.vessel_type}</p>
                      <p className="text-xs font-bold mb-2">{v.name}</p>
                      <div className="flex justify-between text-[10px] border-t border-white/5 pt-2">
                        <span className="text-slate-400">Risk Score</span>
                        <span className={v.risk_score > 0.4 ? 'text-rose-400' : 'text-emerald-400'}>
                          {(v.risk_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className={`p-1.5 rounded-full border-2 border-white shadow-lg transition-transform hover:scale-125 ${
                    v.status === 'Critical' ? 'bg-rose-500 animate-pulse' : 
                    v.status === 'Warning' ? 'bg-amber-500' : 'bg-emerald-500'
                  }`}>
                    <Ship className="text-white" size={14} />
                  </div>
                </div>
              </Marker>
            ))}
          </Map>
        </div>

        {/* Live Incident Ticker */}
        <div className="glass-card flex flex-col h-[500px]">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="text-[10px] font-bold text-slate-800 uppercase tracking-wider flex items-center">
              <Activity size={14} className="mr-2 text-brand-primary" />
              Live Fleet Activity
            </h3>
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {fleet.filter(v => v.status !== 'Normal').map((v, i) => (
              <div key={i} className={`p-3 rounded-xl border animate-in slide-in-from-right-4 duration-300 ${
                v.status === 'Critical' ? 'bg-rose-50 border-rose-100' : 'bg-amber-50 border-amber-100'
              }`}>
                <div className="flex justify-between items-start mb-1">
                  <span className={`text-[9px] font-bold uppercase ${
                    v.status === 'Critical' ? 'text-rose-600' : 'text-amber-600'
                  }`}>
                    {v.status} ALERT
                  </span>
                  <span className="text-[8px] text-slate-400 font-bold">JUST NOW</span>
                </div>
                <p className="text-xs font-bold text-slate-800">{v.name}</p>
                <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                  {v.status === 'Critical' ? 'Potential impact detected. Initiating emergency stabilization.' : 'High sea state detected. Speed reduction recommended.'}
                </p>
              </div>
            ))}
            {fleet.filter(v => v.status === 'Normal').slice(0, 5).map((v, i) => (
              <div key={i} className="p-3 rounded-xl border border-slate-50 bg-slate-50/30">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-[9px] font-bold text-emerald-600 uppercase">NORMAL</span>
                  <span className="text-[8px] text-slate-400 font-bold">STABLE</span>
                </div>
                <p className="text-xs font-bold text-slate-800">{v.name}</p>
                <p className="text-[10px] text-slate-500 mt-1">Sailing as scheduled towards {v.destination}.</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FleetView;
