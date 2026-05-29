import React from 'react';
import { api } from '../services/api';
import type { StreamData } from '../types';
import SignalChart from './SignalChart';
import MapTracker from './MapTracker';
import { Activity, AlertCircle, Shield, Anchor, Compass, Play } from 'lucide-react';

interface LiveViewProps {
  data: StreamData | null;
  signalBuffer: number[];
  connected: boolean;
}

const LiveView: React.FC<LiveViewProps> = ({ data, signalBuffer, connected }) => {
  const handleStartVoyage = async () => {
    try {
      await api.startVoyage();
    } catch (error) {
      console.error("Failed to start voyage:", error);
    }
  };

  const getStatusConfig = (pred: number) => {
    switch (pred) {
      case 0: return { color: '#059669', text: 'text-emerald-600', icon: Shield };
      case 2: return { color: '#be123c', text: 'text-rose-700', icon: AlertCircle };
      default: return { color: '#d97706', text: 'text-amber-600', icon: AlertCircle };
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Live Streaming</h1>
          <p className="text-slate-500 mt-1">Real-time telemetry and instantaneous crash detection.</p>
        </div>
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-full border ${connected ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-rose-50 border-rose-100 text-rose-700'}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-[10px] font-bold uppercase tracking-wider">{connected ? 'Live' : 'Offline'}</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-8 relative">
          {/* Map Integration */}
          {data?.telemetry && (
            <MapTracker 
              lat={data.telemetry.lat} 
              lng={data.telemetry.lng} 
              location={data.telemetry.location} 
            />
          )}

          {/* Start Voyage Overlay */}
          {data && !data.is_active && (
            <div className="absolute inset-0 z-10 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center rounded-3xl border border-white/10">
              <div className="text-center p-8 glass-card max-w-sm border-white/20 bg-white/10 shadow-2xl">
                <div className="w-16 h-16 bg-brand-primary rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg shadow-indigo-500/50">
                   <Anchor className="text-white" size={32} />
                </div>
                <h2 className="text-white text-xl font-bold mb-2">Ready to Depart</h2>
                <p className="text-slate-300 text-xs mb-8 leading-relaxed">
                   Voyage plan for <span className="text-brand-secondary font-black">{data.route_name || "Standard Maritime Route"}</span> is loaded and ready. 
                   Initiate the sequence to start real-time monitoring.
                </p>
                <button 
                  onClick={handleStartVoyage}
                  className="group w-full flex items-center justify-center space-x-3 py-4 bg-white text-slate-900 rounded-2xl font-black text-sm uppercase tracking-wider hover:bg-brand-primary hover:text-white transition-all transform hover:scale-105 active:scale-95 shadow-xl"
                >
                  <Play size={18} className="fill-current" />
                  <span>Start Voyage</span>
                </button>
              </div>
            </div>
          )}
          
          <SignalChart 
            data={signalBuffer} 
            title="Accelerometer Stream (G-Force)" 
            color={data ? getStatusConfig(data.prediction).color : "#6366f1"}
          />
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Active Voyage</h3>
            <p className="text-xs font-bold text-slate-800 mb-6">{data?.route_name || "Syncing Route..."}</p>
            
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-8">Active State</h3>
            
            {!data ? (
              <div className="flex flex-col items-center justify-center py-12 text-slate-300">
                <Activity className="animate-pulse mb-3" size={32} />
                <p className="text-xs font-bold uppercase tracking-wider">Waiting</p>
              </div>
            ) : (
              <div className="space-y-8">
                <div className="text-center">
                  <div className={`inline-flex p-4 rounded-2xl mb-4 bg-slate-50 ${getStatusConfig(data.prediction).text}`}>
                    {React.createElement(getStatusConfig(data.prediction).icon, { size: 40 })}
                  </div>
                  <h2 className={`text-2xl font-black tracking-tight ${getStatusConfig(data.prediction).text}`}>{data.label}</h2>
                  <p className="text-slate-400 text-[10px] font-bold uppercase mt-2 tracking-wider">Classification</p>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-end">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Certainty</span>
                    <span className="text-xl font-black text-slate-800">{(data.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-300 ${data.confidence > 0.7 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                      style={{ width: `${data.confidence * 100}%` }}
                    />
                  </div>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Protocol Action</p>
                  <p className="text-xs font-bold text-slate-700 leading-relaxed">{data.alert}</p>
                </div>
              </div>
            )}
          </div>

          <div className="glass-card p-6">
             <div className="flex items-center space-x-2 mb-6">
                <Anchor size={16} className="text-brand-primary" />
                <h3 className="text-[10px] font-bold text-slate-800 uppercase tracking-wider">Vessel Status</h3>
             </div>
             {data?.telemetry ? (
               <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-500 font-medium">Vessel</span>
                    <span className="text-xs text-slate-900 font-bold">{data.telemetry.vessel}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-500 font-medium">Speed</span>
                    <span className="text-xs text-slate-900 font-bold">22.4 kn</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-500 font-medium">Region</span>
                    <span className="text-xs text-slate-900 font-bold">{data.telemetry.location}</span>
                  </div>
                  <div className="pt-2 border-t border-slate-50 flex items-center space-x-2 text-emerald-500">
                    <Compass size={12} />
                    <span className="text-[10px] font-bold uppercase">On Schedule</span>
                  </div>
               </div>
             ) : (
               <div className="text-center py-4 text-slate-300 text-xs italic">Syncing GPS...</div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveView;
