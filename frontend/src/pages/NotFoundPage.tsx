import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="screen-state">
      <p className="auth-eyebrow">404</p>
      <h1>Page not found</h1>
      <p>The route you requested does not exist in this frontend module.</p>
      <Link className="primary-button" to="/login">
        Go to login
      </Link>
    </main>
  );
}
