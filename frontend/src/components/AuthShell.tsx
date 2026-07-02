import type { PropsWithChildren } from "react";
import { Link } from "react-router-dom";

interface AuthShellProps extends PropsWithChildren {
  eyebrow: string;
  title: string;
  description: string;
  alternatePrompt: string;
  alternateLinkText: string;
  alternateLinkTo: string;
}

export function AuthShell({
  eyebrow,
  title,
  description,
  alternatePrompt,
  alternateLinkText,
  alternateLinkTo,
  children,
}: AuthShellProps) {
  return (
    <main className="auth-shell">
      <section className="auth-hero">
        <p className="auth-eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="auth-copy">{description}</p>
        <div className="auth-insight-grid">
          <article>
            <span>JWT Sessions</span>
            <strong>Secure API access with bearer tokens</strong>
          </article>
          <article>
            <span>Protected Routes</span>
            <strong>Route guards keep private screens private</strong>
          </article>
          <article>
            <span>Live Portfolio</span>
            <strong>Ready for dashboards, analytics, and holdings</strong>
          </article>
        </div>
      </section>

      <section className="auth-panel">
        {children}
        <p className="auth-switch">
          {alternatePrompt}{" "}
          <Link to={alternateLinkTo}>{alternateLinkText}</Link>
        </p>
      </section>
    </main>
  );
}
