export interface PortfolioHoldingRow {
  id: number;
  symbol: string;
  quantity: string;
  purchase_price: string;
  current_price: string;
  profit_loss: string;
}

export interface CreateHoldingRequest {
  symbol: string;
  quantity: string;
  purchase_price: string;
  purchase_date: string;
}
