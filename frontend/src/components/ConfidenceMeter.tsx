import React from 'react';

interface ConfidenceMeterProps {
  confidence: number; // 0.0 to 1.0
  isSynthetic: boolean | null;
  label?: string;
  showThreshold?: boolean;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  confidence,
  isSynthetic,
  label = 'Model Confidence',
  showThreshold = true
}) => {
  const percentage = Math.round(confidence * 100);

  let barColor = 'bg-slate-500';
  let textColor = 'text-slate-400';

  if (isSynthetic === true) {
    if (confidence >= 0.85) {
      barColor = 'bg-red-500';
      textColor = 'text-red-400';
    } else if (confidence >= 0.70) {
      barColor = 'bg-orange-500';
      textColor = 'text-orange-400';
    } else {
      barColor = 'bg-amber-500';
      textColor = 'text-amber-400';
    }
  } else if (isSynthetic === false) {
    barColor = 'bg-emerald-500';
    textColor = 'text-emerald-400';
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-medium text-cyber-muted tracking-wide">{label}</span>
        <span className={`text-sm font-bold font-mono ${textColor}`}>
          {percentage}% {isSynthetic ? 'Synthetic' : isSynthetic === false ? 'Authentic' : ''}
        </span>
      </div>

      <div className="relative w-full h-3 bg-cyber-surface rounded-full overflow-hidden border border-cyber-border">
        {/* Fill bar */}
        <div
          className={`h-full ${barColor} transition-all duration-700 ease-out`}
          style={{ width: `${percentage}%` }}
        />
        {/* 50% Threshold marker */}
        {showThreshold && (
          <div
            className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-slate-400/40 z-10"
            title="Decision Threshold (50%)"
          />
        )}
      </div>

      {showThreshold && (
        <div className="flex justify-between text-[10px] text-cyber-muted mt-1 font-mono">
          <span>0%</span>
          <span className="text-slate-500">Threshold 50%</span>
          <span>100%</span>
        </div>
      )}
    </div>
  );
};
