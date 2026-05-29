import { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import RiskAssessmentView from './components/RiskAssessmentView';
import AnalysisView from './components/AnalysisView';
import LiveView from './components/LiveView';
import HistoryView from './components/HistoryView';
import FleetView from './components/FleetView';
import { WS_URL } from './services/api';
import type { StreamData } from './types';

function App() {
  const [activeTab, setActiveTab] = useState('fleet');
  const [hasError, setHasError] = useState(false);

  // Global Voyage State
  const [streamData, setStreamData] = useState<StreamData | null>(null);
  const [signalBuffer, setSignalBuffer] = useState<number[]>([]);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    socketRef.current = new WebSocket(WS_URL);
    socketRef.current.onopen = () => setConnected(true);
    socketRef.current.onclose = () => setConnected(false);
    socketRef.current.onmessage = (event) => {
      const parsed: StreamData = JSON.parse(event.data);
      setStreamData(parsed);
      if (parsed.is_active) {
        setSignalBuffer(prev => [...prev, ...parsed.signal].slice(-250));
      }
    };
    return () => socketRef.current?.close();
  }, []);

  // Simple error boundary effect
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error("Caught error:", error);
      setHasError(true);
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Application Error</h1>
          <p className="text-gray-600 mb-6">Something went wrong while loading the dashboard. Please check the browser console (F12) for details.</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-primary-blue text-white px-6 py-2 rounded-xl font-bold hover:bg-primary-dark transition-all"
          >
            Reload Application
          </button>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'fleet':
        return <FleetView />;
      case 'risk':
        return <RiskAssessmentView setActiveTab={setActiveTab} />;
      case 'analysis':
        return <AnalysisView />;
      case 'live':
        return <LiveView data={streamData} signalBuffer={signalBuffer} connected={connected} />;
      case 'history':
        return <HistoryView />;
      default:
        return <FleetView />;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#FAF8F3]">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 ml-64 p-8 transition-all duration-300">
        <div className="max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
