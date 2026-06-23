import React, { useState, useEffect } from 'react';
import { Ship, Package, Layers, Info } from 'lucide-react';

interface VoyageFormProps {
  onAssess: (data: any) => void;
  loading: boolean;
}

const PORTS = [
  // Asia
  { name: "Shanghai (CNSHA), China", lat: 31.23, lng: 121.47 },
  { name: "Singapore (SGSIN), Singapore", lat: 1.29, lng: 103.85 },
  { name: "Ningbo-Zhoushan (CNNGB), China", lat: 29.86, lng: 121.55 },
  { name: "Shenzhen (CNSZX), China", lat: 22.54, lng: 114.05 },
  { name: "Guangzhou (CNCAN), China", lat: 23.12, lng: 113.26 },
  { name: "Busan (KRPUS), South Korea", lat: 35.17, lng: 129.07 },
  { name: "Qingdao (CNTAO), China", lat: 36.06, lng: 120.38 },
  { name: "Hong Kong (HKHKG), Hong Kong", lat: 22.31, lng: 114.16 },
  { name: "Tianjin (CNTSN), China", lat: 39.08, lng: 117.20 },
  { name: "Port Klang (MYPKG), Malaysia", lat: 3.00, lng: 101.40 },
  { name: "Tanjung Pelepas (MYTPP), Malaysia", lat: 1.36, lng: 103.55 },
  { name: "Laem Chabang (THLCH), Thailand", lat: 13.08, lng: 100.88 },
  { name: "Kaohsiung (TWKHH), Taiwan", lat: 22.61, lng: 120.31 },
  { name: "Yokohama (JPYOK), Japan", lat: 35.44, lng: 139.63 },
  { name: "Tokyo (JPTOK), Japan", lat: 35.68, lng: 139.69 },
  { name: "Colombo (LKCMB), Sri Lanka", lat: 6.92, lng: 79.86 },
  { name: "Mumbai (INBOM), India", lat: 18.94, lng: 72.83 },
  { name: "Ho Chi Minh City (VNSGN), Vietnam", lat: 10.82, lng: 106.63 },
  
  // Middle East
  { name: "Jebel Ali (AEJEA), UAE", lat: 25.01, lng: 55.06 },
  { name: "Salalah (OMSLL), Oman", lat: 16.94, lng: 53.99 },
  
  // Europe
  { name: "Rotterdam (NLRTM), Netherlands", lat: 51.92, lng: 4.47 },
  { name: "Antwerp (BEANR), Belgium", lat: 51.27, lng: 4.38 },
  { name: "Hamburg (DEHAM), Germany", lat: 53.55, lng: 9.99 },
  { name: "Bremen/Bremerhaven (DEBRV), Germany", lat: 53.54, lng: 8.58 },
  { name: "Valencia (ESVLC), Spain", lat: 39.46, lng: -0.32 },
  { name: "Algeciras (ESALG), Spain", lat: 36.13, lng: -5.44 },
  { name: "Felixstowe (GBFXT), UK", lat: 51.96, lng: 1.34 },
  
  // North America
  { name: "Los Angeles (USLAX), USA", lat: 33.77, lng: -118.19 },
  { name: "Long Beach (USLGB), USA", lat: 33.75, lng: -118.22 },
  { name: "New York/New Jersey (USNYC), USA", lat: 40.71, lng: -74.00 },
  { name: "Savannah (USSAV), USA", lat: 32.08, lng: -81.09 },
  { name: "Seattle (USSEA), USA", lat: 47.60, lng: -122.33 },
  { name: "Vancouver (CAVAN), Canada", lat: 49.28, lng: -123.12 },
  { name: "Houston (USHOU), USA", lat: 29.76, lng: -95.36 },
  { name: "Oakland (USOAK), USA", lat: 37.80, lng: -122.27 },
  
  // South America
  { name: "Santos (BRSSZ), Brazil", lat: -23.96, lng: -46.33 },
  { name: "Callao (PECLL), Peru", lat: -12.05, lng: -77.14 },
  { name: "Cartagena (COCTG), Colombia", lat: 10.39, lng: -75.48 },
  
  // Africa
  { name: "Tangier Med (MAPTM), Morocco", lat: 35.88, lng: -5.50 },
  { name: "Port Said (EGPSD), Egypt", lat: 31.26, lng: 32.30 },
  { name: "Durban (OMDUB), South Africa", lat: -29.85, lng: 31.02 },
  
  // Oceania
  { name: "Sydney (AUSYD), Australia", lat: -33.86, lng: 151.20 },
  { name: "Melbourne (AUMEL), Australia", lat: -37.81, lng: 144.96 },
  { name: "Auckland (NZAKL), New Zealand", lat: -36.84, lng: 174.76 }
].sort((a, b) => a.name.localeCompare(b.name));

const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
  const R = 6371; // Earth radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

const VoyageForm: React.FC<VoyageFormProps> = ({ onAssess, loading }) => {
  const [formData, setFormData] = useState({
    origin: PORTS[0],
    destination: PORTS[1],
    departure_date: new Date().toISOString().split('T')[0],
    arrival_date: '',
    cargo_fragility: 0.5,
    container_count: 500,
    alignment_score: 0.9
  });

  // Automatically calculate ETA
  useEffect(() => {
    if (formData.origin && formData.destination && formData.departure_date) {
      const distanceKm = calculateDistance(
        formData.origin.lat, formData.origin.lng,
        formData.destination.lat, formData.destination.lng
      );
      
      // Speed in knots (22) converted to km/h (1 knot approx 1.852 km/h)
      const speedKmH = 22 * 1.852;
      const travelHours = distanceKm / speedKmH;
      
      // Add 20% buffer for weather and port congestion
      const totalHours = travelHours * 1.2;
      
      const departure = new Date(formData.departure_date);
      const arrival = new Date(departure.getTime() + totalHours * 3600000);
      
      setFormData(prev => ({
        ...prev,
        arrival_date: arrival.toISOString().split('T')[0]
      }));
    }
  }, [formData.origin, formData.destination, formData.departure_date]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAssess(formData);
  };

  const handlePortChange = (type: 'origin' | 'destination', portName: string) => {
    const port = PORTS.find(p => p.name === portName);
    if (port) {
      setFormData({ ...formData, [type]: port });
    }
  };

  return (
    <div className="glass-card p-8">
      <div className="flex items-center space-x-3 mb-8">
        <div className="bg-brand-primary/10 p-2 rounded-lg text-brand-primary">
          <Ship size={20} />
        </div>
        <h2 className="text-xl font-bold text-slate-800">Voyage Setup</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-1">Origin Port</label>
            <select 
              value={formData.origin.name}
              onChange={e => handlePortChange('origin', e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all cursor-pointer"
            >
              {PORTS.map(port => (
                <option key={port.name} value={port.name}>{port.name}</option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-1">Destination Port</label>
            <select 
              value={formData.destination.name}
              onChange={e => handlePortChange('destination', e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all cursor-pointer"
            >
              {PORTS.map(port => (
                <option key={port.name} value={port.name}>{port.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-1">Departure Date</label>
            <input 
              type="date" 
              value={formData.departure_date}
              onChange={e => setFormData({...formData, departure_date: e.target.value})}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all"
            />
          </div>
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-1">Arrival Date</label>
            <input 
              type="date" 
              value={formData.arrival_date}
              onChange={e => setFormData({...formData, arrival_date: e.target.value})}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          <div className="space-y-2">
            <div className="flex items-center space-x-2 mb-1 ml-1">
               <Package size={14} className="text-slate-400" />
               <label className="text-[10px] font-bold text-slate-400 uppercase">Fragility Index</label>
            </div>
            <input 
              type="range" min="0.1" max="1.0" step="0.1"
              value={formData.cargo_fragility}
              onChange={e => setFormData({...formData, cargo_fragility: parseFloat(e.target.value)})}
              className="w-full accent-brand-primary"
            />
            <div className="flex justify-between text-[10px] font-bold text-slate-400 px-1">
              <span>Stable</span>
              <span className="text-brand-primary">{formData.cargo_fragility}</span>
              <span>Fragile</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2 mb-1 ml-1">
               <Layers size={14} className="text-slate-400" />
               <label className="text-[10px] font-bold text-slate-400 uppercase">Load (TEU)</label>
            </div>
            <input 
              type="number" 
              value={formData.container_count}
              onChange={e => setFormData({...formData, container_count: parseInt(e.target.value) || 1})}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm font-medium outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2 mb-1 ml-1">
               <Info size={14} className="text-slate-400" />
               <label className="text-[10px] font-bold text-slate-400 uppercase">Stack Stability</label>
            </div>
            <input 
              type="range" min="0.5" max="1.0" step="0.05"
              value={formData.alignment_score}
              onChange={e => setFormData({...formData, alignment_score: parseFloat(e.target.value)})}
              className="w-full accent-brand-primary"
            />
            <div className="flex justify-between text-[10px] font-bold text-slate-400 px-1">
              <span>Unstable</span>
              <span className="text-brand-primary">{(formData.alignment_score * 100).toFixed(0)}%</span>
              <span>Optimal</span>
            </div>
          </div>
        </div>

        <button 
          type="submit"
          disabled={loading}
          className="w-full bg-brand-primary text-white py-4 rounded-2xl font-black text-sm uppercase tracking-wider hover:bg-brand-dark transition-all disabled:opacity-50 shadow-xl shadow-indigo-100 mt-6"
        >
          {loading ? "Calculating Probabilities..." : "Assess Voyage Risk"}
        </button>
      </form>
    </div>
  );
};

export default VoyageForm;
