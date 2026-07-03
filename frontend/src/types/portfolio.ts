export interface PortfolioHoldingRow {
  id: number;
  symbol: string;
  quantity: string;
  purchase_price: string;
  current_price: string;
  profit_loss: string;
  is_live_price: boolean;
  price_source: "live" | "cached" | "purchase";
}

export interface CreateHoldingRequest {
  symbol: string;
  quantity: string;
  purchase_price: string;
  purchase_date: string;
}
