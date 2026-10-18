import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Filter,
  RefreshCw,
  Film,
  Mic,
  Image as ImageIcon,
  ChevronLeft,
  ChevronRight,
  Layers
} from 'lucide-react';
import { getAnalyses } from '../services/api';
import type { AnalysisSummary } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const AnalysisHistory: React.FC = () => {
  const [items, setItems] = useState<AnalysisSummary[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [search, setSearch] = useState<string>('');
  const [mediaType, setMediaType] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [riskLevel, setRiskLevel] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await getAnalyses({
        page,
        pageSize,
        search: search || undefined,
        mediaType: mediaType || undefined,
        status: statusFilter || undefined,
        riskLevel: riskLevel || undefined
      });
      setItems(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, mediaType, statusFilter, riskLevel]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Forensic Case Repository
          </h1>
          <p className="mt-1 text-sm text-cyber-muted">
            Search, filter, and audit all historic media verifications and model predictions.
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="self-start sm:self-auto p-2.5 rounded-lg bg-cyber-card border border-cyber-border text-slate-300 hover:text-white"
          title="Refresh list"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl p-4 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-cyber-muted" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by original filename..."
              className="w-full pl-9 pr-4 py-2 rounded-lg bg-cyber-surface border border-cyber-border text-sm text-white placeholder-cyber-muted focus:outline-none focus:border-cyber-accent"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-cyber-accent text-cyber-bg font-semibold text-xs hover:bg-cyber-accent/90"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap gap-3 pt-2 text-xs">
          {/* Media Type Filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-cyber-muted">Type:</span>
            <select
              value={mediaType}
              onChange={(e) => {
                setMediaType(e.target.value);
                setPage(1);
              }}
              className="bg-cyber-surface border border-cyber-border rounded-md px-2 py-1 text-white text-xs focus:outline-none"
            >
              <option value="">All Types</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="audio">Audio</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-cyber-muted">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="bg-cyber-surface border border-cyber-border rounded-md px-2 py-1 text-white text-xs focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="queued">Queued</option>
              <option value="failed">Failed</option>
              <option value="model_unavailable">Model Unavailable</option>
            </select>
          </div>

          {/* Risk Level Filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-cyber-muted">Risk:</span>
            <select
              value={riskLevel}
              onChange={(e) => {
                setRiskLevel(e.target.value);
                setPage(1);
              }}
              className="bg-cyber-surface border border-cyber-border rounded-md px-2 py-1 text-white text-xs focus:outline-none"
            >
              <option value="">All Risk Levels</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {(mediaType || statusFilter || riskLevel || search) && (
            <button
              onClick={() => {
                setMediaType('');
                setStatusFilter('');
                setRiskLevel('');
                setSearch('');
                setPage(1);
              }}
              className="text-cyber-accent hover:underline text-xs ml-auto"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Case Table */}
      <div className="bg-cyber-card border border-cyber-border rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-cyber-muted space-y-2">
            <RefreshCw className="w-6 h-6 animate-spin text-cyber-accent mx-auto" />
            <p className="text-xs font-mono">Fetching records...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-cyber-muted">
            <Layers className="w-10 h-10 mx-auto text-slate-600 mb-3" />
            <p className="text-sm">No analysis records matching the selected criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-cyber-surface text-cyber-muted uppercase font-mono tracking-wider border-b border-cyber-border">
                <tr>
                  <th className="px-5 py-3">File / Subject</th>
                  <th className="px-5 py-3">Media</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Verdict</th>
                  <th className="px-5 py-3">Risk</th>
                  <th className="px-5 py-3">Confidence</th>
                  <th className="px-5 py-3">Timestamp</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyber-border/40">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-cyber-surface/40 transition-colors">
                    <td className="px-5 py-4 font-medium text-white max-w-xs truncate">
                      {item.original_filename}
                    </td>
                    <td className="px-5 py-4">
                      <span className="inline-flex items-center space-x-1 uppercase font-mono text-[10px] text-cyber-muted bg-cyber-surface px-2 py-0.5 rounded border border-cyber-border">
                        {item.media_type === 'image' && <ImageIcon className="w-3 h-3 text-sky-400" />}
                        {item.media_type === 'video' && <Film className="w-3 h-3 text-purple-400" />}
                        {item.media_type === 'audio' && <Mic className="w-3 h-3 text-emerald-400" />}
                        <span>{item.media_type}</span>
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge verdict={item.overall_prediction} />
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge risk={item.risk_level} />
                    </td>
                    <td className="px-5 py-4 font-mono">
                      {item.overall_confidence > 0
                        ? `${Math.round(item.overall_confidence * 100)}%`
                        : '—'}
                    </td>
                    <td className="px-5 py-4 text-cyber-muted font-mono text-[11px]">
                      {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <Link
                        to={`/analyses/${item.id}`}
                        className="text-cyber-accent hover:text-white font-medium text-xs transition-colors"
                      >
                        Inspect &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="p-4 border-t border-cyber-border flex items-center justify-between text-xs text-cyber-muted">
          <span>
            Showing {items.length > 0 ? (page - 1) * pageSize + 1 : 0} to{' '}
            {Math.min(page * pageSize, total)} of {total} cases
          </span>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-md bg-cyber-surface border border-cyber-border text-slate-300 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-white px-2">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-md bg-cyber-surface border border-cyber-border text-slate-300 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
