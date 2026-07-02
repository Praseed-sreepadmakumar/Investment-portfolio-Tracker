import api from "./api";
import type {
  CreateHoldingRequest,
  PortfolioHoldingRow,
} from "../types/portfolio";

export async function getPortfolioOverview(): Promise<PortfolioHoldingRow[]> {
  const response = await api.get<PortfolioHoldingRow[]>("/portfolio/overview");
  return response.data;
}

export async function addHolding(values: CreateHoldingRequest): Promise<void> {
  await api.post("/portfolio", values);
}

export async function deleteHolding(holdingId: number): Promise<void> {
  await api.delete(`/portfolio/${holdingId}`);
}
