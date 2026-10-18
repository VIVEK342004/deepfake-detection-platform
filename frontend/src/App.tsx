import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { NewAnalysis } from './pages/NewAnalysis';
import { AnalysisDetails } from './pages/AnalysisDetails';
import { AnalysisHistory } from './pages/AnalysisHistory';
import { SystemStatus } from './pages/SystemStatus';
import { Methodology } from './pages/Methodology';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-cyber-bg text-slate-100 flex flex-col font-sans selection:bg-cyber-accent selection:text-cyber-bg">
        {/* Navigation Bar */}
        <Navbar />

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/new" element={<NewAnalysis />} />
            <Route path="/analyses/:id" element={<AnalysisDetails />} />
            <Route path="/history" element={<AnalysisHistory />} />
            <Route path="/system" element={<SystemStatus />} />
            <Route path="/about" element={<Methodology />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Professional Cybersecurity Footer */}
        <footer className="border-t border-cyber-border/70 bg-cyber-surface/60 py-6 text-xs text-cyber-muted">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white tracking-wider">VERITAS<span className="text-cyber-accent">AI</span></span>
              <span>&bull;</span>
              <span>Enterprise Multimodal Deepfake Forensic Platform</span>
            </div>
            <div className="flex items-center space-x-4 text-[11px] font-mono">
              <span className="text-slate-400">STATUS: OPERATIONAL</span>
              <span>&bull;</span>
              <span>PYTORCH + FASTAPI + REACT</span>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
