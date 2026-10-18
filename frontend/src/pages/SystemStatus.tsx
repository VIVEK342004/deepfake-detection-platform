import React, { useState, useEffect } from 'react';
import {
  Server,
  Cpu,
  Layers,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  HardDrive,
  Sliders,
  ShieldCheck,
  Info
} from 'lucide-react';
import { getSystemStatus, getHealth } from '../services/api';
import type { SystemStatusResponse, HealthResponse } from '../types';

export const SystemStatus: React.FC = () => {
  const [system, setSystem] = useState<SystemStatusResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sysRes, healthRes] = await Promise.all([
        getSystemStatus(),
        getHealth()
      ]);
      setSystem(sysRes);
      setHealth(healthRes);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            System & Neural Infrastructure
          </h1>
          <p className="mt-1 text-sm text-cyber-muted">
            Hardware acceleration, model checkpoint verification, and operational constraints.
          </p>
        </div>

        <button
          onClick={fetchStatus}
          disabled={loading}
          className="self-start sm:self-auto flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-cyber-card border border-cyber-border text-slate-300 hover:text-white"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span className="text-xs">Refresh Health</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Backend & Hardware Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-cyber-muted">API Core</span>
            <Server className="w-5 h-5 text-cyber-blue" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  health?.status === 'healthy' ? 'bg-emerald-400' : 'bg-red-400'
                }`}
              />
              <span className="text-lg font-bold font-mono text-white uppercase">
                {health?.status || 'OFFLINE'}
              </span>
            </div>
            <p className="text-xs text-cyber-muted mt-1 font-mono">
              FastAPI {health?.version || '1.0.0'} &bull; Env: {health?.environment || 'dev'}
            </p>
          </div>
        </div>

        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-cyber-muted">Inference Hardware</span>
            <Cpu className="w-5 h-5 text-cyber-accent" />
          </div>
          <div>
            <span className="text-lg font-bold font-mono text-white uppercase">
              {system?.device?.toUpperCase() || 'CPU'}
            </span>
            <p className="text-xs text-cyber-muted mt-1 truncate">
              {system?.gpu_available ? system.gpu_name : 'Optimized CPU Multi-threading'}
            </p>
          </div>
        </div>

        <div className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-cyber-muted">Database & Storage</span>
            <HardDrive className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-semibold text-white">Storage Persistent</span>
            </div>
            <p className="text-xs text-cyber-muted mt-1 font-mono">
              DB Connected: {health?.database_connected ? 'YES' : 'NO'} &bull; Max: {system?.limits.max_upload_size_mb || 50}MB
            </p>
          </div>
        </div>
      </div>

      {/* Model Checkpoint Cards */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-white">
          Deployed Neural Model Cards
        </h3>

        <div className="grid grid-cols-1 gap-4">
          {system?.models.map((model) => (
            <div
              key={model.name}
              className="bg-cyber-card border border-cyber-border rounded-xl p-5 space-y-4 hover:border-cyber-border/80 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-cyber-border pb-3">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-cyber-surface border border-cyber-border text-cyber-accent">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white text-sm">{model.name}</h4>
                    <p className="text-xs text-cyber-muted font-mono">
                      Architecture: {model.architecture} &bull; Modality: {model.modality}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium font-mono ${
                      model.is_ready
                        ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800'
                        : 'bg-amber-950/70 text-amber-400 border border-amber-800'
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 mr-1.5 rounded-full ${
                        model.is_ready ? 'bg-emerald-400' : 'bg-amber-400'
                      }`}
                    />
                    {model.status.toUpperCase()}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {model.description}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs bg-cyber-surface/60 p-3 rounded-lg border border-cyber-border font-mono">
                <div>
                  <span className="text-cyber-muted block text-[10px]">CHECKPOINT STATUS</span>
                  <span className="text-white">
                    {model.checkpoint_found ? 'Verified & Loaded' : 'Missing File'}
                  </span>
                </div>
                <div>
                  <span className="text-cyber-muted block text-[10px]">PARAMETERS</span>
                  <span className="text-white">
                    {model.parameters_count ? `${model.parameters_count.toLocaleString()} params` : 'Heuristic/N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-cyber-muted block text-[10px]">DEVICE ALLOCATION</span>
                  <span className="text-cyber-accent">{model.device}</span>
                </div>
              </div>

              {model.limitations && model.limitations.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-[11px] font-semibold text-cyber-muted uppercase tracking-wider block">
                    Documented Operational Constraints:
                  </span>
                  <ul className="text-xs text-cyber-muted space-y-1 list-disc list-inside">
                    {model.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
