import { useEffect, useMemo, useState } from "react";

import { AssetAllocationChart } from "../components/AssetAllocationChart";
import { BackButton } from "../components/BackButton";
import { DashboardCard } from "../components/DashboardCard";
import { getApiErrorMessage } from "../context/AuthContext";
import { useAuth } from "../hooks/useAuth";
import { getAllocation } from "../services/analytics";
import { getDashboardMetrics } from "../services/dashboard";
import type { AllocationItem } from "../types/analytics";
import type { DashboardMetrics } from "../types/dashboard";

function toCurrency(value: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(Number(value));
}

function toPercent(value: string) {
  return `${Number(value).toFixed(2)}%`;
}

export function DashboardPage() {
  const { logout, user } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [allocation, setAllocation] = useState<AllocationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const joinedDate = useMemo(() => {
    if (!user) {
      return "";
    }

    return new Intl.DateTimeFormat("en", {
      dateStyle: "medium",
    }).format(new Date(user.created_at));
  }, [user]);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setErrorMessage("");
      setIsLoading(true);

      try {
        const [dashboardData, allocationData] = await Promise.all([
          getDashboardMetrics(),
          getAllocation(),
        ]);
        if (active) {
          setMetrics(dashboardData);
          setAllocation(allocationData);
        }
      } catch (error) {
        if (active) {
          setErrorMessage(getApiErrorMessage(error));
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      active = false;
    };
  }, []);

  const profitValue = Number(metrics?.total_profit_loss ?? "0");
  const profitTone =
    profitValue > 0 ? "positive" : profitValue < 0 ? "negative" : "neutral";

  const returnValue = Number(metrics?.return_percentage ?? "0");
  const returnTone =
    returnValue > 0 ? "positive" : returnValue < 0 ? "negative" : "neutral";

  return (
    <main className="dashboard-shell">
      <section className="dashboard-panel dashboard-panel--hero">
        <div>
          <p className="auth-eyebrow">Protected Workspace</p>
          <h1>{user?.username}, your session is active.</h1>
          <p className="auth-copy">
            Live metrics are loaded from your protected dashboard API using
            Axios and rendered as reusable cards.
          </p>
        </div>
        <div className="hero-actions">
          <BackButton fallbackTo="/portfolio" />
          <button className="secondary-button" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </section>

      {isLoading ? (
        <section className="dashboard-panel dashboard-panel--state">
          <div className="spinner" aria-hidden="true" />
          <p>Loading dashboard metrics...</p>
        </section>
      ) : null}

      {!isLoading && errorMessage ? (
        <section className="dashboard-panel dashboard-panel--state">
          <p className="form-error">{errorMessage}</p>
        </section>
      ) : null}

      {!isLoading && !errorMessage && metrics ? (
        <>
          <section className="dashboard-card-grid">
            <DashboardCard
              label="Total Investment"
              value={toCurrency(metrics.total_investment)}
              hint="Amount you invested."
            />
            <DashboardCard
              label="Current Value"
              value={toCurrency(metrics.current_portfolio_value)}
              hint="Current market value."
            />
            <DashboardCard
              label="Profit"
              value={toCurrency(metrics.total_profit_loss)}
              hint="Gain or loss so far."
              tone={profitTone}
            />
            <DashboardCard
              label="Return %"
              value={toPercent(metrics.return_percentage)}
              hint="Profit or loss percentage."
              tone={returnTone}
            />
            <DashboardCard
              label="Holdings Count"
              value={String(metrics.number_of_holdings)}
              hint="Total stocks in portfolio."
            />
          </section>

          <section className="dashboard-grid">
            <article className="dashboard-panel">
              <span className="metric-label">Email</span>
              <strong>{user?.email}</strong>
              <p>Your account email.</p>
            </article>
            <article className="dashboard-panel">
              <span className="metric-label">Member Since</span>
              <strong>{joinedDate || "Just now"}</strong>
              <p>Your account creation date.</p>
            </article>
          </section>

          <section className="dashboard-panel">
            <div className="chart-header">
              <span className="metric-label">Asset Allocation</span>
              <h2>Portfolio Distribution</h2>
              <p>Stock allocation based on current portfolio percentages.</p>
            </div>
            <AssetAllocationChart data={allocation} />
          </section>
        </>
      ) : null}
    </main>
  );
}
