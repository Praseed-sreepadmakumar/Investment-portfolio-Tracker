import type { PortfolioHoldingRow } from "../types/portfolio";

interface HoldingsTableProps {
  rows: PortfolioHoldingRow[];
  onDelete: (holdingId: number) => Promise<void>;
  deletingId: number | null;
}

function toCurrency(value: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(value));
}

function toQuantity(value: string) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 4,
  }).format(Number(value));
}

function getPriceSourceBadge(row: PortfolioHoldingRow): {
  label: string;
  title: string;
  tone: "cached" | "purchase";
} | null {
  if (row.price_source === "cached") {
    return {
      label: "cached",
      title: "Live quote unavailable; using last saved live price.",
      tone: "cached",
    };
  }

  if (row.price_source === "purchase") {
    return {
      label: "purchase",
      title:
        "Live quote unavailable and no saved live price exists yet; using purchase price.",
      tone: "purchase",
    };
  }

  return null;
}

export function HoldingsTable({
  rows,
  onDelete,
  deletingId,
}: HoldingsTableProps) {
  if (!rows.length) {
    return (
      <section className="portfolio-empty">
        <p>No holdings yet. Add your first stock using the form above.</p>
      </section>
    );
  }

  return (
    <section className="holdings-table-wrap">
      <table className="holdings-table">
        <thead>
          <tr>
            <th>Stock Symbol</th>
            <th>Quantity</th>
            <th>Purchase Price</th>
            <th>Current Price</th>
            <th>Profit/Loss</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const profit = Number(row.profit_loss);
            const tone =
              profit > 0 ? "positive" : profit < 0 ? "negative" : "neutral";
            const sourceBadge = getPriceSourceBadge(row);

            return (
              <tr key={row.id}>
                <td data-label="Stock Symbol">{row.symbol}</td>
                <td data-label="Quantity">{toQuantity(row.quantity)}</td>
                <td data-label="Purchase Price">
                  {toCurrency(row.purchase_price)}
                </td>
                <td data-label="Current Price">
                  <span className="current-price-cell">
                    <span>{toCurrency(row.current_price)}</span>
                    {sourceBadge ? (
                      <span
                        className={`price-source-badge price-source-badge--${sourceBadge.tone}`}
                        title={sourceBadge.title}
                      >
                        {sourceBadge.label}
                      </span>
                    ) : null}
                  </span>
                </td>
                <td data-label="Profit/Loss">
                  <span className={`profit-chip profit-chip--${tone}`}>
                    {toCurrency(row.profit_loss)}
                  </span>
                </td>
                <td data-label="Action">
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => onDelete(row.id)}
                    disabled={deletingId === row.id}
                  >
                    {deletingId === row.id ? "Deleting..." : "Delete"}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
