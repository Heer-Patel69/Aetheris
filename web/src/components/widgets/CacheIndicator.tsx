interface Props {
  hot: number;
  warm: number;
  cold: number;
}

export default function CacheIndicator({ hot, warm, cold }: Props) {
  return (
    <div className="cache-indicator">
      <div className="cache-tier hot">🔥 {hot} Hot</div>
      <div className="cache-tier warm">🌡️ {warm} Warm</div>
      <div className="cache-tier cold">❄️ {cold} Cold</div>
    </div>
  );
}
