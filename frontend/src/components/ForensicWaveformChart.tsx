import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine
} from 'recharts';

interface ChartDataPoint {
  label: string | number;
  syntheticProbability: number;
  threshold: number;
}

interface ForensicChartProps {
  data: ChartDataPoint[];
  title: string;
  xLabel?: string;
}

export const ForensicWaveformChart: React.FC<ForensicChartProps> = ({
  data,
  title,
  xLabel = 'Temporal Timeline (s)'
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="p-6 text-center text-cyber-muted text-sm border border-dashed border-cyber-border rounded-xl">
        No sequential temporal datapoints available.
      </div>
    );
  }

  return (
    <div className="bg-cyber-surface/60 border border-cyber-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          {title}
        </h4>
        <div className="flex items-center space-x-3 text-[11px] font-mono text-cyber-muted">
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 bg-red-500 rounded-sm inline-block" />
            <span>Synthetic Prob</span>
          </span>
          <span className="flex items-center space-x-1">
            <span className="w-2.5 h-0.5 bg-amber-400 inline-block" />
            <span>50% Threshold</span>
          </span>
        </div>
      </div>

      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="probGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="label"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: '#1f2b45' }}
            />
            <YAxis
              domain={[0, 1]}
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: '#1f2b45' }}
              tickFormatter={(v) => `${Math.round(v * 100)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0e1422',
                borderColor: '#1f2b45',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#f8fafc'
              }}
              formatter={(val: number) => [`${Math.round(val * 100)}%`, 'Synthetic Score']}
              labelFormatter={(lbl) => `Position: ${lbl}`}
            />
            <ReferenceLine y={0.5} stroke="#f59e0b" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="syntheticProbability"
              stroke="#ef4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#probGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[10px] text-right text-cyber-muted mt-2 font-mono">
        {xLabel}
      </p>
    </div>
  );
};
