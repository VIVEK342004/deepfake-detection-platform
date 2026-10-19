
import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from 'react-router-dom';

import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { NewAnalysis } from './pages/NewAnalysis';
import { AnalysisDetails } from './pages/AnalysisDetails';
import { AnalysisHistory } from './pages/AnalysisHistory';
import { SystemStatus } from './pages/SystemStatus';
import { Methodology } from './pages/Methodology';
import { Login } from './pages/Login';
import { isAuthenticated } from './services/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const location = useLocation();

  if (!isAuthenticated()) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  return <>{children}</>;
};

const AppLayout: React.FC = () => {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  return (
    <div className="min-h-screen bg-cyber-bg text-slate-100 flex flex-col font-sans selection:bg-cyber-accent selection:text-cyber-bg">
      {!isLoginPage && <Navbar />}

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated() ? (
                <Navigate to="/" replace />
              ) : (
                <Login />
              )
            }
          />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/new"
            element={
              <ProtectedRoute>
                <NewAnalysis />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analyses/:id"
            element={
              <ProtectedRoute>
                <AnalysisDetails />
              </ProtectedRoute>
            }
          />

          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <AnalysisHistory />
              </ProtectedRoute>
            }
          />

          <Route path="/system" element={<SystemStatus />} />
          <Route path="/about" element={<Methodology />} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {!isLoginPage && (
        <footer className="border-t border-cyber-border/70 bg-cyber-surface/60 py-6 text-xs text-cyber-muted">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white tracking-wider">
                VERITAS<span className="text-cyber-accent">AI</span>
              </span>
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
      )}
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
};

export default App;
