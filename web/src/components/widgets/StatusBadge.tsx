interface Props {
  status: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  label: string;
  pulse?: boolean;
}

export default function StatusBadge({ status, label, pulse = false }: Props) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      {pulse && <span className="status-dot" />}
      {label}
    </span>
  );
}
