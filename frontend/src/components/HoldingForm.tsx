import { useState } from "react";

import { FormField } from "./FormField";
import type { CreateHoldingRequest } from "../types/portfolio";

interface HoldingFormProps {
  onSubmit: (values: CreateHoldingRequest) => Promise<void>;
  isSubmitting: boolean;
}

export function HoldingForm({ onSubmit, isSubmitting }: HoldingFormProps) {
  const [values, setValues] = useState<CreateHoldingRequest>({
    symbol: "",
    quantity: "",
    purchase_price: "",
    purchase_date: new Date().toISOString().slice(0, 10),
  });

  function setField<K extends keyof CreateHoldingRequest>(
    key: K,
    value: CreateHoldingRequest[K],
  ) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(values);
    setValues((current) => ({
      ...current,
      symbol: "",
      quantity: "",
      purchase_price: "",
    }));
  }

  return (
    <form className="holding-form" onSubmit={handleSubmit}>
      <FormField
        label="Stock Symbol"
        name="symbol"
        value={values.symbol}
        onChange={(event) =>
          setField("symbol", event.target.value.toUpperCase())
        }
        placeholder="AAPL"
        required
      />
      <FormField
        label="Quantity"
        name="quantity"
        type="number"
        min="0.0001"
        step="0.0001"
        value={values.quantity}
        onChange={(event) => setField("quantity", event.target.value)}
        required
      />
      <FormField
        label="Purchase Price"
        name="purchase_price"
        type="number"
        min="0.01"
        step="0.01"
        value={values.purchase_price}
        onChange={(event) => setField("purchase_price", event.target.value)}
        required
      />
      <FormField
        label="Purchase Date"
        name="purchase_date"
        type="date"
        value={values.purchase_date}
        onChange={(event) => setField("purchase_date", event.target.value)}
        required
      />

      <button className="primary-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Adding..." : "Add Holding"}
      </button>
    </form>
  );
}
