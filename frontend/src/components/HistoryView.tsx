import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { EventLog } from '../types';
import { EVENT_LABELS } from '../types';
import { ShieldCheck, AlertCircle, AlertTriangle, Clock } from 'lucide-react';

const HistoryView: React.FC = () => {
  const [logs, setLogs] = useState<EventLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      setError(null);
      try {
        const data = await api.getHistory();
        setLogs(data);
      } catch (err: any) {
        console.error("Error fetching logs:", err);
        setError("Failed to fetch event history. Please verify the backend is online.");
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const getStatusBadge = (label: number) => {
    switch (label) {
      case 0: return { icon: ShieldCheck, color: 'text-emerald-600 bg-emerald-50 border-emerald-100' };
      case 2: return { icon: AlertCircle, color: 'text-rose-600 bg-rose-50 border-rose-100' };
      default: return { icon: AlertTriangle, color: 'text-amber-600 bg-amber-50 border-amber-100' };
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary"></div></div>;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Event History</h1>
        <p className="text-slate-500 mt-1">Audit log of all detected impact events.</p>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center space-x-2">
          <AlertTriangle size={18} />
          <div>
            <p className="font-semibold text-sm">History Error</p>
            <p className="text-xs">{error}</p>
          </div>
        </div>
      )}

      <div className="glass-card overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-100">
              <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Date & Time</th>
              <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Classification</th>
              <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">ML Confidence</th>
              <th className="px-6 py-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Protocol Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {logs.map((log) => {
              const badge = getStatusBadge(log.predicted_label);
              return (
                <tr key={log.id} className="hover:bg-slate-50/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2.5 text-slate-600">
                      <Clock size={14} className="text-slate-400" />
                      <span className="text-xs font-semibold">{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border text-[10px] font-bold ${badge.color}`}>
                      <badge.icon size={12} />
                      <span>{EVENT_LABELS[log.predicted_label]}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-bold text-slate-700 w-8">{(log.confidence * 100).toFixed(0)}%</span>
                      <div className="w-24 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-slate-300"
                          style={{ width: `${log.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-xs font-bold text-slate-500">{log.alert}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {logs.length === 0 && (
          <div className="p-20 text-center text-slate-300">
            <ShieldCheck className="mx-auto mb-4 opacity-20" size={48} />
            <p className="text-xs font-bold uppercase tracking-wider">No Events Found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryView;
