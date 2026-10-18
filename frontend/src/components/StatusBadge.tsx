import React from 'react';
import type { AnalysisStatus, PredictionVerdict, RiskLevel } from '../types';

interface StatusBadgeProps {
  status?: AnalysisStatus;
  risk?: RiskLevel;
  verdict?: PredictionVerdict;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, risk, verdict }) => {
  if (risk) {
    switch (risk) {
      case 'critical':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-950/80 text-red-400 border border-red-800">
            CRITICAL RISK
          </span>
        );
      case 'high':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-950/80 text-orange-400 border border-orange-800">
            HIGH RISK
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800">
            MEDIUM RISK
          </span>
        );
      case 'low':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
            LOW RISK
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            UNKNOWN
          </span>
        );
    }
  }

  if (verdict) {
    switch (verdict) {
      case 'likely_synthetic':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/30">
            LIKELY SYNTHETIC / DEEPFAKE
          </span>
        );
      case 'likely_authentic':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            LIKELY AUTHENTIC
          </span>
        );
      case 'inconclusive':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            INCONCLUSIVE
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
            UNPROCESSED
          </span>
        );
    }
  }

  if (status) {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-300 border border-emerald-800/60">
            <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-emerald-400"></span>
            Completed
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-950/60 text-blue-300 border border-blue-800/60">
            <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-blue-400 animate-pulse"></span>
            Processing
          </span>
        );
      case 'queued':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
            <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-slate-400"></span>
            Queued
          </span>
        );
      case 'model_unavailable':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-950/60 text-purple-300 border border-purple-800/60">
            <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-purple-400"></span>
            Model Unavailable
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-950/60 text-red-300 border border-red-800/60">
            <span className="w-1.5 h-1.5 mr-1.5 rounded-full bg-red-400"></span>
            Failed
          </span>
        );
      default:
        return null;
    }
  }

  return null;
};
