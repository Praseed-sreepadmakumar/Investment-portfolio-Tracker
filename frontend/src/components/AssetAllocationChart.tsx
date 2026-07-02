import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import type { AllocationItem } from "../types/analytics";

interface AssetAllocationChartProps {
  data: AllocationItem[];
}

const CHART_COLORS = [
  "#0F766E",
  "#2563EB",
  "#B45309",
  "#7C3AED",
  "#DC2626",
  "#15803D",
  "#C2410C",
  "#334155",
];

export function AssetAllocationChart({ data }: AssetAllocationChartProps) {
  const chartData = data.map((item) => ({
    name: item.company_name,
    value: Number(item.percentage),
  }));

  if (!chartData.length) {
    return (
      <div className="chart-empty-state">
        <p>No allocation data yet. Add holdings to view allocation.</p>
      </div>
    );
  }

  return (
    <div className="allocation-chart-wrap">
      <ResponsiveContainer width="100%" height={340}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="45%"
            innerRadius={58}
            outerRadius={110}
            dataKey="value"
            nameKey="name"
            stroke="rgba(255, 255, 255, 0.9)"
            strokeWidth={2}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`${entry.name}-${index}`}
                fill={CHART_COLORS[index % CHART_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${Number(value ?? 0).toFixed(2)}%`} />
          <Legend verticalAlign="bottom" height={36} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
