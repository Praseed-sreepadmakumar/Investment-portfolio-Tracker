import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { AuthShell } from "../components/AuthShell";
import { FormField } from "../components/FormField";
import { getApiErrorMessage } from "../context/AuthContext";
import { useAuth } from "../hooks/useAuth";

export function RegisterPage() {
  const { isAuthenticated, register } = useAuth();
  const navigate = useNavigate();
  const [formValues, setFormValues] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  function updateField(
    field: "username" | "email" | "password",
    value: string,
  ) {
    setFormValues((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");
    setIsSubmitting(true);

    try {
      await register(formValues);
      setSuccessMessage("Account created. Redirecting you to login...");
      window.setTimeout(() => {
        navigate("/login", { replace: true });
      }, 900);
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell
      eyebrow="New Investor Setup"
      title="Create your workspace"
      description="Start with a secure account, then connect your holdings, analytics, and market-aware dashboard experience."
      alternatePrompt="Already registered?"
      alternateLinkText="Go to login"
      alternateLinkTo="/login"
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <header className="form-header">
          <h2>Register</h2>
          <p>
            Create a new account to access your protected portfolio workspace.
          </p>
        </header>

        <FormField
          label="Username"
          name="username"
          value={formValues.username}
          onChange={(event) => updateField("username", event.target.value)}
          placeholder="Choose a username"
          autoComplete="username"
          required
        />
        <FormField
          label="Email"
          name="email"
          type="email"
          value={formValues.email}
          onChange={(event) => updateField("email", event.target.value)}
          placeholder="you@example.com"
          autoComplete="email"
          required
        />
        <FormField
          label="Password"
          name="password"
          type="password"
          value={formValues.password}
          onChange={(event) => updateField("password", event.target.value)}
          placeholder="At least 8 characters"
          autoComplete="new-password"
          required
        />

        {errorMessage ? <div className="form-error">{errorMessage}</div> : null}
        {successMessage ? (
          <div className="form-success">{successMessage}</div>
        ) : null}

        <button
          className="primary-button"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>
    </AuthShell>
  );
}
