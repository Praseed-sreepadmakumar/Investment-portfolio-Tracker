import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { BackButton } from "../components/BackButton";
import { HoldingForm } from "../components/HoldingForm";
import { HoldingsTable } from "../components/HoldingsTable";
import { getApiErrorMessage } from "../context/AuthContext";
import { useAuth } from "../hooks/useAuth";
import {
  addHolding,
  deleteHolding,
  getPortfolioOverview,
} from "../services/portfolio";
import type {
  CreateHoldingRequest,
  PortfolioHoldingRow,
} from "../types/portfolio";

export function PortfolioPage() {
  const { logout, user } = useAuth();
  const [rows, setRows] = useState<PortfolioHoldingRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const loadPortfolio = useCallback(async () => {
    setErrorMessage("");
    setIsLoading(true);

    try {
      const data = await getPortfolioOverview();
      setRows(data);
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPortfolio();
  }, [loadPortfolio]);

  async function handleAddHolding(values: CreateHoldingRequest) {
    setErrorMessage("");
    setIsAdding(true);

    try {
      await addHolding(values);
      await loadPortfolio();
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error));
    } finally {
      setIsAdding(false);
    }
  }

  async function handleDeleteHolding(holdingId: number) {
    setErrorMessage("");
    setDeletingId(holdingId);

    try {
      await deleteHolding(holdingId);
      await loadPortfolio();
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="dashboard-shell">
      <section className="dashboard-panel dashboard-panel--hero">
        <div>
          <p className="auth-eyebrow">Portfolio</p>
          <h1>{user?.username}, your holdings</h1>
          <p className="auth-copy">
            Track each stock with live market price and profit/loss details.
          </p>
        </div>
        <div className="hero-actions">
          <BackButton fallbackTo="/dashboard" />
          <Link className="secondary-button" to="/dashboard">
            Go to Dashboard
          </Link>
          <button
            className="secondary-button"
            type="button"
            onClick={() => void loadPortfolio()}
          >
            Refresh Portfolio
          </button>
          <button className="secondary-button" type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </section>

      <section className="dashboard-panel">
        <h2 className="section-title">Add Holding</h2>
        <HoldingForm onSubmit={handleAddHolding} isSubmitting={isAdding} />
      </section>

      {isLoading ? (
        <section className="dashboard-panel dashboard-panel--state">
          <div className="spinner" aria-hidden="true" />
          <p>Loading portfolio...</p>
        </section>
      ) : null}

      {!isLoading && errorMessage ? (
        <section className="dashboard-panel dashboard-panel--state">
          <p className="form-error">{errorMessage}</p>
        </section>
      ) : null}

      {!isLoading ? (
        <section className="dashboard-panel">
          <h2 className="section-title">Holdings</h2>
          <HoldingsTable
            rows={rows}
            onDelete={handleDeleteHolding}
            deletingId={deletingId}
          />
        </section>
      ) : null}
    </main>
  );
}
