interface Props {
  label: string;
  value: number;
  max?: number;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export default function ProgressBar({ label, value, max = 100, variant = 'default' }: Props) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  const fillClass = variant === 'default' ? '' : variant;

  return (
    <div className="progress-bar-wrapper">
      <div className="progress-bar-header">
        <span className="progress-bar-label">{label}</span>
        <span className="progress-bar-pct">{pct}%</span>
      </div>
      <div className="progress-bar-track">
        <div className={`progress-bar-fill ${fillClass}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
