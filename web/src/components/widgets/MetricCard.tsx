import type { ReactNode } from 'react'

interface Props {
  label: string;
  value: string | number | null;
  detail?: string;
  icon?: ReactNode;
  accent?: string;
}

export default function MetricCard({ label, value, detail, icon, accent }: Props) {
  return (
    <div className="metric-card animate-in" style={{ '--card-accent': accent } as React.CSSProperties}>
      <div className="metric-card-label">
        {icon}
        {label}
      </div>
      <div className="metric-card-value">{value ?? '—'}</div>
      {detail && <div className="metric-card-detail">{detail}</div>}
    </div>
  );
}
