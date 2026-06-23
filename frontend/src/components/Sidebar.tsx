import React, { useState, useEffect } from 'react';
import { Activity, Radio, History, Shield } from 'lucide-react';
import type { TabId } from '../App';

interface SidebarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const [online, setOnline] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
        const healthUrl = apiBase.replace(/\/api$/, '') + '/health';
        const res = await fetch(healthUrl);
        setOnline(res.ok);
      } catch (e) {
        setOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const menuItems = [
    { id: 'risk', label: 'Risk Assessment', icon: Shield },
    { id: 'analysis', label: 'Analysis', icon: Activity },
    { id: 'live', label: 'Live Stream', icon: Radio },
    { id: 'history', label: 'History', icon: History },
  ] as const;

  return (
    <div className="w-64 bg-slate-900 h-screen fixed left-0 top-0 flex flex-col text-slate-300">
      <div className="p-8 flex items-center space-x-3">
        <div className="bg-brand-primary p-2 rounded-lg">
          <Shield className="text-white" size={24} />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-tight">DetectPro</h1>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Cargo Safety</p>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1.5 mt-4">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              activeTab === item.id
                ? 'bg-brand-primary text-white font-semibold'
                : 'hover:bg-slate-800 hover:text-white'
            }`}
          >
            <item.icon size={18} />
            <span className="text-sm">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-6">
        <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
          <p className="text-[10px] font-bold text-slate-500 uppercase mb-2">System Status</p>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full animate-pulse ${online ? 'bg-status-success' : 'bg-rose-500'}`} />
            <span className="text-xs text-slate-300 font-medium">
              {online ? 'Core API Online' : 'API Offline'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
