import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { ShieldCheck, Activity, PlusCircle, History, Info, Server } from 'lucide-react';
import { getHealth } from '../services/api';

export const Navbar: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const h = await getHealth();
        setIsHealthy(h.status === 'healthy');
      } catch {
        setIsHealthy(false);
      }
    };
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-cyber-surface/90 backdrop-blur-md border-b border-cyber-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <NavLink to="/" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-lg bg-cyber-accent/10 border border-cyber-accent/30 text-cyber-accent group-hover:border-cyber-accent transition-all duration-300">
              <ShieldCheck className="w-6 h-6 text-cyber-accent" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base sm:text-lg text-white tracking-wide">
                  VERITAS<span className="text-cyber-accent">AI</span>
                </span>
                <span className="text-[10px] uppercase font-mono tracking-wider px-1.5 py-0.5 rounded bg-cyber-card text-cyber-blue border border-cyber-border">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-cyber-muted tracking-tight hidden sm:block">
                Multimodal Deepfake Detection System
              </p>
            </div>
          </NavLink>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyber-card text-cyber-accent border border-cyber-border'
                    : 'text-slate-300 hover:text-white hover:bg-cyber-card/50'
                }`
              }
            >
              <Activity className="w-4 h-4" />
              <span className="hidden md:inline">Dashboard</span>
            </NavLink>

            <NavLink
              to="/new"
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyber-accent text-cyber-bg font-semibold'
                    : 'bg-cyber-card text-cyber-accent border border-cyber-accent/30 hover:bg-cyber-accent/10'
                }`
              }
            >
              <PlusCircle className="w-4 h-4" />
              <span>New Analysis</span>
            </NavLink>

            <NavLink
              to="/history"
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyber-card text-cyber-accent border border-cyber-border'
                    : 'text-slate-300 hover:text-white hover:bg-cyber-card/50'
                }`
              }
            >
              <History className="w-4 h-4" />
              <span className="hidden md:inline">History</span>
            </NavLink>

            <NavLink
              to="/system"
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyber-card text-cyber-accent border border-cyber-border'
                    : 'text-slate-300 hover:text-white hover:bg-cyber-card/50'
                }`
              }
            >
              <Server className="w-4 h-4" />
              <span className="hidden md:inline">System & Models</span>
            </NavLink>

            <NavLink
              to="/about"
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyber-card text-cyber-accent border border-cyber-border'
                    : 'text-slate-300 hover:text-white hover:bg-cyber-card/50'
                }`
              }
            >
              <Info className="w-4 h-4" />
              <span className="hidden md:inline">Methodology</span>
            </NavLink>

            {/* Health Heartbeat */}
            <div className="pl-2 flex items-center">
              <div
                title={isHealthy ? 'Backend Operational' : 'Backend Connecting/Offline'}
                className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-cyber-card border border-cyber-border"
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    isHealthy === null
                      ? 'bg-amber-400 animate-pulse'
                      : isHealthy
                      ? 'bg-emerald-400'
                      : 'bg-red-400 animate-ping'
                  }`}
                />
                <span className="text-[11px] text-slate-400 hidden lg:inline">
                  {isHealthy ? 'API ONLINE' : 'API OFFLINE'}
                </span>
              </div>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
};
