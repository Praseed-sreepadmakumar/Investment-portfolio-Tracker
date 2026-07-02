interface DashboardCardProps {
  label: string;
  value: string;
  hint: string;
  tone?: "neutral" | "positive" | "negative";
}

export function DashboardCard({
  label,
  value,
  hint,
  tone = "neutral",
}: DashboardCardProps) {
  return (
    <article className={`dashboard-card dashboard-card--${tone}`}>
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>
      <p>{hint}</p>
    </article>
  );
}
