import api from "./api";
import type { DashboardMetrics } from "../types/dashboard";

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  const response = await api.get<DashboardMetrics>("/dashboard");
  return response.data;
}
