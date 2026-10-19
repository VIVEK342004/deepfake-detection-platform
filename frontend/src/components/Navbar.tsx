
import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Activity,
  PlusCircle,
  History,
  Info,
  Server,
  LogOut,
} from 'lucide-react';
import { getHealth } from '../services/api';
import { isAuthenticated, logoutUser } from '../services/auth';

export const Navbar: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;

    const check = async () => {
      try {
        const health = await getHealth();
        if (active) setIsHealthy(health.status === 'healthy');
      } catch {
        if (active) setIsHealthy(false);
      }
    };

    void check();
    const interval = setInterval(() => void check(), 15000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const handleLogout = () => {
    logoutUser();
    navigate('/login', { replace: true });
  };

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-cyber-card text-cyber-accent border border-cyber-border'
        : 'text-slate-300 hover:text-white hover:bg-cyber-card/50'
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-cyber-border bg-cyber-surface/90 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-3">
          <NavLink to="/" className="group flex shrink-0 items-center space-x-3">
            <div className="rounded-lg border border-cyber-accent/30 bg-cyber-accent/10 p-2 text-cyber-accent transition-all duration-300 group-hover:border-cyber-accent">
              <ShieldCheck className="h-6 w-6" />
            </div>

            <div>
              <div className="flex items-center space-x-2">
                <span className="text-base font-bold tracking-wide text-white sm:text-lg">
                  VERITAS<span className="text-cyber-accent">AI</span>
                </span>
                <span className="rounded border border-cyber-border bg-cyber-card px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-cyber-blue">
                  v1.0
                </span>
              </div>
              <p className="hidden text-[11px] tracking-tight text-cyber-muted sm:block">
                Multimodal Deepfake Detection System
              </p>
            </div>
          </NavLink>

          <nav className="flex items-center justify-end gap-1 sm:gap-2">
            <NavLink to="/" end className={linkClass} title="Dashboard">
              <Activity className="h-4 w-4" />
              <span className="hidden md:inline">Dashboard</span>
            </NavLink>

            <NavLink
              to="/new"
              className={({ isActive }) =>
                `flex items-center space-x-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyber-accent font-semibold text-cyber-bg'
                    : 'border border-cyber-accent/30 bg-cyber-card text-cyber-accent hover:bg-cyber-accent/10'
                }`
              }
            >
              <PlusCircle className="h-4 w-4" />
              <span className="hidden sm:inline">New Analysis</span>
            </NavLink>

            <NavLink to="/history" className={linkClass} title="Analysis History">
              <History className="h-4 w-4" />
              <span className="hidden md:inline">History</span>
            </NavLink>

            <NavLink to="/system" className={linkClass} title="System and Models">
              <Server className="h-4 w-4" />
              <span className="hidden lg:inline">System & Models</span>
            </NavLink>

            <NavLink to="/about" className={linkClass} title="Methodology">
              <Info className="h-4 w-4" />
              <span className="hidden lg:inline">Methodology</span>
            </NavLink>

            <div className="flex items-center pl-1 sm:pl-2">
              <div
                title={
                  isHealthy === null
                    ? 'Checking backend'
                    : isHealthy
                    ? 'Backend operational'
                    : 'Backend offline or unreachable'
                }
                className="flex items-center gap-1.5 rounded-full border border-cyber-border bg-cyber-card px-2 py-1.5 font-mono text-xs"
              >
                <span
                  className={`h-2 w-2 rounded-full ${
                    isHealthy === null
                      ? 'animate-pulse bg-amber-400'
                      : isHealthy
                      ? 'bg-emerald-400'
                      : 'bg-red-400'
                  }`}
                />
                <span className="hidden text-[11px] text-slate-400 xl:inline">
                  {isHealthy === null
                    ? 'CHECKING'
                    : isHealthy
                    ? 'API ONLINE'
                    : 'API OFFLINE'}
                </span>
              </div>
            </div>

            {isAuthenticated() && (
              <button
                type="button"
                onClick={handleLogout}
                title="Sign out of your account"
                className="flex items-center gap-1.5 rounded-md border border-red-500/30 bg-red-500/10 px-2.5 py-2 text-sm font-medium text-red-300 transition-colors hover:border-red-400 hover:bg-red-500/20 hover:text-red-200 sm:px-3"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
