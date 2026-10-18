import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  variant?: 'default' | 'accent' | 'danger' | 'warning' | 'success';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default'
}) => {
  const variantStyles = {
    default: 'text-cyber-blue bg-cyber-blue/10 border-cyber-border',
    accent: 'text-cyber-accent bg-cyber-accent/10 border-cyber-accent/30',
    danger: 'text-cyber-danger bg-cyber-danger/10 border-cyber-danger/30',
    warning: 'text-cyber-warning bg-cyber-warning/10 border-cyber-warning/30',
    success: 'text-cyber-success bg-cyber-success/10 border-cyber-success/30'
  };

  return (
    <div className="bg-cyber-card/70 border border-cyber-border rounded-xl p-5 hover:border-cyber-border/80 transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-cyber-muted">
          {title}
        </span>
        <div className={`p-2 rounded-lg border ${variantStyles[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-3">
        <span className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white">
          {value}
        </span>
        {subtitle && (
          <p className="mt-1 text-xs text-cyber-muted truncate">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};
