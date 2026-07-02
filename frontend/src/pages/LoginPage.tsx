import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { AuthShell } from "../components/AuthShell";
import { FormField } from "../components/FormField";
import { getApiErrorMessage } from "../context/AuthContext";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const redirectTo =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname ?? "/portfolio";

  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await login({ username, password });
      navigate(redirectTo, { replace: true });
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Investment Portfolio Tracker"
      title="Welcome back"
      description="Sign in to manage holdings, analytics, and dashboard insights from a single secure workspace."
      alternatePrompt="Need an account?"
      alternateLinkText="Create one"
      alternateLinkTo="/register"
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <header className="form-header">
          <h2>Login</h2>
          <p>Use your username and password to continue.</p>
        </header>

        <FormField
          label="Username"
          name="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="e.g. ada_portfolio"
          autoComplete="username"
          required
        />
        <FormField
          label="Password"
          name="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter your password"
          autoComplete="current-password"
          required
        />

        {errorMessage ? <div className="form-error">{errorMessage}</div> : null}

        <button
          className="primary-button"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </AuthShell>
  );
}
