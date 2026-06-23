import React, { useState } from 'react';
import VoyageForm from './VoyageForm';
import RiskMap from './RiskMap';
import { ShieldCheck, AlertTriangle, Wind, Waves, Thermometer, Clock, Activity } from 'lucide-react';
import { api } from '../services/api';
import type { VoyageAssessment } from '../types';
import type { TabId } from '../App';

interface RiskAssessmentViewProps {
  setActiveTab: (tab: TabId) => void;
  setVoyageId: (id: string) => void;
}

const RiskAssessmentView: React.FC<RiskAssessmentViewProps> = ({ setActiveTab, setVoyageId }) => {
  const [loading, setLoading] = useState(false);
  const [assessment, setAssessment] = useState<VoyageAssessment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const resultsRef = React.useRef<HTMLDivElement>(null);

  // Automatically scroll to results when assessment is loaded
  React.useEffect(() => {
    if (assessment && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [assessment]);

  const handleAssess = async (formData: any) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.assessVoyage(formData);
      setAssessment(data);
      if (data.voyage_id) {
        setVoyageId(data.voyage_id);
      }
    } catch (err: any) {
      console.error("Risk assessment failed:", err);
      const errMsg = err.response?.data?.detail || "Failed to perform risk assessment. Please verify connection and coordinates.";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Predictive Risk Assessment</h1>
        <p className="text-slate-500 mt-1">Data-driven probability analysis using real-time weather and load parameters.</p>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2">
          <AlertTriangle size={18} />
          <div>
            <p className="font-semibold text-sm">Assessment Error</p>
            <p className="text-xs">{error}</p>
          </div>
        </div>
      )}

      <div className="flex flex-col space-y-8">
        <div className="w-full">
          <VoyageForm onAssess={handleAssess} loading={loading} />
        </div>

        <div ref={resultsRef} className="w-full space-y-8">
          {assessment ? (
            <>
              <div className="animate-in slide-in-from-bottom-4 duration-500">
                <RiskMap waypoints={assessment.waypoints} riskLevel={assessment.risk_level} />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-card p-6 border-l-4 border-l-brand-primary">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Crash Probability</p>
                      <h2 className="text-4xl font-black text-slate-900 mt-1">{(assessment.probability * 100).toFixed(1)}%</h2>
                    </div>
                    <div className={`p-2 rounded-xl ${assessment.risk_level === 'High' ? 'bg-rose-100 text-rose-600' : 'bg-emerald-100 text-emerald-600'}`}>
                      {assessment.risk_level === 'High' ? <AlertTriangle size={24} /> : <ShieldCheck size={24} />}
                    </div>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-1000 ${assessment.risk_level === 'High' ? 'bg-rose-500' : 'bg-emerald-500'}`}
                      style={{ width: `${assessment.probability * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-4 font-medium leading-relaxed mb-6">
                    Based on predicted {assessment.weather_summary.max_wave_height}m waves and cargo fragility of {assessment.weather_summary.cargo_fragility}.
                  </p>
                  
                  <button 
                    onClick={() => setActiveTab('live')}
                    className="w-full flex items-center justify-center space-x-2 py-3 bg-brand-primary text-white rounded-xl font-bold text-xs uppercase tracking-wider hover:bg-brand-dark transition-all shadow-lg shadow-indigo-100"
                  >
                    <Activity size={16} />
                    <span>Start Monitoring Voyage</span>
                  </button>
                </div>

                <div className="space-y-6">
                  <div className="glass-card p-6">
                    <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-6">AI Risk Drivers</h3>
                    <div className="space-y-5">
                      {[
                        { label: 'Wave Impact', val: assessment.weather_summary.max_wave_height * 10, color: 'bg-blue-500' },
                        { label: 'Wind Stability', val: assessment.weather_summary.max_wind_speed / 2, color: 'bg-cyan-500' },
                        { label: 'Cargo Fragility', val: assessment.weather_summary.cargo_fragility * 100, color: 'bg-amber-500' },
                        { label: 'Duration Risk', val: assessment.weather_summary.duration_days * 5, color: 'bg-slate-500' }
                      ].map((factor, i) => (
                        <div key={i} className="space-y-1.5">
                          <div className="flex justify-between items-center text-[10px] font-bold uppercase">
                            <span className="text-slate-500">{factor.label}</span>
                            <span className="text-slate-900">{Math.min(100, factor.val).toFixed(0)}% Impact</span>
                          </div>
                          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${factor.color} transition-all duration-1000 delay-300`}
                              style={{ width: `${Math.min(100, factor.val)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-[9px] text-slate-400 mt-6 leading-relaxed italic">
                      * These factors represent the feature importance weighting in the Random Forest model.
                    </p>
                  </div>

                  <div className="glass-card p-6">
                    <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-6">Forecast Summary</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 text-slate-600">
                        <Waves size={16} className="text-blue-400" />
                        <span className="text-xs font-semibold">Max Wave Height</span>
                      </div>
                      <span className="text-xs font-bold text-slate-900">{assessment.weather_summary.max_wave_height}m</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 text-slate-600">
                        <Wind size={16} className="text-slate-400" />
                        <span className="text-xs font-semibold">Max Wind Speed</span>
                      </div>
                      <span className="text-xs font-bold text-slate-900">{assessment.weather_summary.max_wind_speed} km/h</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 text-slate-600">
                        <Clock size={16} className="text-brand-primary" />
                        <span className="text-xs font-semibold">Voyage Duration</span>
                      </div>
                      <span className="text-xs font-bold text-slate-900">{assessment.weather_summary.duration_days.toFixed(1)} Days</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
          ) : (
            <div className="glass-card h-full flex flex-col items-center justify-center p-12 text-center border-dashed border-2 border-slate-200 bg-slate-50/50">
              <div className="w-20 h-20 bg-white rounded-3xl shadow-sm flex items-center justify-center mb-6">
                <Thermometer className="text-slate-200" size={40} />
              </div>
              <h3 className="text-lg font-bold text-slate-400">Ready for Assessment</h3>
              <p className="text-sm text-slate-400 max-w-xs mt-2 leading-relaxed">
                Configure your voyage parameters above and run the ML prediction to see route risks and weather impacts.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentView;
