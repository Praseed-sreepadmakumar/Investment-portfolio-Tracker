import { useNavigate } from "react-router-dom";

interface BackButtonProps {
  fallbackTo: string;
  label?: string;
}

export function BackButton({ fallbackTo, label = "Back" }: BackButtonProps) {
  const navigate = useNavigate();

  function handleBack() {
    const historyIndex = window.history.state?.idx;

    // React Router stores navigation depth in history.state.idx.
    if (typeof historyIndex === "number" && historyIndex > 0) {
      navigate(-1);
      return;
    }

    navigate(fallbackTo, { replace: true });
  }

  return (
    <button className="secondary-button" type="button" onClick={handleBack}>
      {label}
    </button>
  );
}
