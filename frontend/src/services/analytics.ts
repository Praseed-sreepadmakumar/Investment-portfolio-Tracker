import api from "./api";
import type { AllocationItem } from "../types/analytics";

export async function getAllocation(): Promise<AllocationItem[]> {
  const response = await api.get<AllocationItem[]>("/allocation");
  return response.data;
}
