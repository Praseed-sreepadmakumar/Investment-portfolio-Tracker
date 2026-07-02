import type { InputHTMLAttributes } from "react";

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function FormField({ label, error, id, ...props }: FormFieldProps) {
  const fieldId = id ?? props.name;

  return (
    <label className="form-field" htmlFor={fieldId}>
      <span>{label}</span>
      <input id={fieldId} {...props} />
      {error ? <small>{error}</small> : null}
    </label>
  );
}
