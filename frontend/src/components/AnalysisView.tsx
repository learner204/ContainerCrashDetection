import React, { useState } from 'react';
import { api } from '../services/api';
import type { AnalysisResult } from '../types';
import { EVENT_LABELS } from '../types';
import SignalChart from './SignalChart';
import { Search, Zap, Info, AlertTriangle } from 'lucide-react';

const AnalysisView: React.FC = () => {
  const [selectedLabel, setSelectedLabel] = useState<number>(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyze(selectedLabel);
      setResult(data);
    } catch (err: any) {
      console.error("Error analyzing signal:", err);
      const errMsg = err.response?.data?.detail || "Failed to analyze signal. Please try again.";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (pred: number) => {
    switch (pred) {
      case 0: return { color: '#10b981', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' };
      case 2: return { color: '#ef4444', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' };
      default: return { color: '#f59e0b', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' };
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Signal Analysis</h1>
        <p className="text-slate-500 mt-1">Simulate sensor events and validate detection parameters.</p>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2">
          <AlertTriangle size={18} />
          <div>
            <p className="font-semibold text-sm">Analysis Error</p>
            <p className="text-xs">{error}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="glass-card p-8 flex flex-col sm:flex-row items-end gap-4">
            <div className="flex-1 w-full">
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Simulate Scenario</label>
              <select 
                value={selectedLabel}
                onChange={(e) => setSelectedLabel(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-primary/20 transition-all text-sm font-medium"
              >
                {Object.entries(EVENT_LABELS).map(([id, label]) => (
                  <option key={id} value={id}>{label}</option>
                ))}
              </select>
            </div>
            <button 
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full sm:w-auto bg-brand-primary text-white px-8 py-3 rounded-xl font-bold flex items-center justify-center space-x-2 hover:bg-brand-dark transition-all disabled:opacity-50 shadow-md shadow-indigo-100"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Search size={18} />
                  <span>Run Analysis</span>
                </>
              )}
            </button>
          </div>

          {result && (
            <SignalChart 
              data={result.signal} 
              title={`Live Telemetry: ${result.label}`} 
              color={getStatusConfig(result.prediction).color}
            />
          )}
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-6">Real-time Result</h3>
            
            {!result ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Info className="text-slate-300" size={24} />
                </div>
                <p className="text-slate-400 text-xs font-medium">Select a scenario to analyze</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Prediction</p>
                  <p className={`text-xl font-black ${getStatusConfig(result.prediction).text}`}>{result.label}</p>
                </div>

                <div>
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">ML Confidence</p>
                  <div className="flex items-center space-x-3">
                    <p className="text-2xl font-black text-slate-800">{(result.confidence * 100).toFixed(0)}%</p>
                    <div className="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-brand-primary transition-all duration-1000"
                        style={{ width: `${result.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className={`p-4 rounded-xl border ${getStatusConfig(result.prediction).bg} ${getStatusConfig(result.prediction).border} ${getStatusConfig(result.prediction).text}`}>
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertTriangle size={14} />
                    <p className="text-[10px] font-bold uppercase">System Alert</p>
                  </div>
                  <p className="text-xs font-semibold leading-relaxed">{result.alert}</p>
                </div>
              </div>
            )}
          </div>

          <div className="bg-slate-900 p-6 rounded-2xl text-white shadow-xl">
            <div className="flex items-center space-x-2 mb-4">
              <Zap size={18} className="text-brand-primary" />
              <h3 className="text-sm font-bold">Simulator Hint</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed font-medium">
              High-confidence "Severe Crash" results automatically trigger the persistent logging system.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisView;
