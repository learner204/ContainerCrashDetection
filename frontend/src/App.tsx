import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import RiskAssessmentView from './components/RiskAssessmentView';
import AnalysisView from './components/AnalysisView';
import LiveView from './components/LiveView';
import HistoryView from './components/HistoryView';

export type TabId = 'risk' | 'analysis' | 'live' | 'history';

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('risk');
  const [hasError, setHasError] = useState(false);
  const [voyageId, setVoyageId] = useState<string | null>(null);

  // Simple error boundary effect
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error("Caught error:", error);
      setHasError(true);
    };
    const handleRejection = (event: PromiseRejectionEvent) => {
      console.error("Unhandled rejection:", event);
      setHasError(true);
    };
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleRejection);
    };
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

  const handleTabChange = (tab: TabId) => {
    if (tab === 'risk') {
      setVoyageId(null);
    }
    setActiveTab(tab);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'risk':
        return <RiskAssessmentView setActiveTab={handleTabChange} setVoyageId={setVoyageId} />;
      case 'analysis':
        return <AnalysisView />;
      case 'live':
        return <LiveView voyageId={voyageId} />;
      case 'history':
        return <HistoryView />;
      default:
        return <RiskAssessmentView setActiveTab={handleTabChange} setVoyageId={setVoyageId} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#FAF8F3]">
      <Sidebar activeTab={activeTab} setActiveTab={handleTabChange} />
      <main className="flex-1 ml-64 p-8 transition-all duration-300">
        <div className="max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
