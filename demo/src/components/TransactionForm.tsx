import { useState } from "react";
import { demoCustomers, demoProducts } from "../data/demoData";
import {
  calculateTransaction,
  validateTransactionInput,
} from "../utils/transactionUtils";
import type { DealSize, Transaction } from "../types/transaction";
import "./TransactionForm.css";

interface TransactionFormProps {
  onSave: (transaction: Transaction) => void;
}

function getLocalDate(): string {
  const today = new Date();
  const offset = today.getTimezoneOffset();
  return new Date(today.getTime() - offset * 60_000).toISOString().slice(0, 10);
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

export default function TransactionForm({ onSave }: TransactionFormProps) {
  const [customerCode, setCustomerCode] = useState("");
  const [productCode, setProductCode] = useState("");
  const [orderDate, setOrderDate] = useState(getLocalDate());
  const [quantity, setQuantity] = useState("1");
  const [sellingPrice, setSellingPrice] = useState("");
  const [dealSize, setDealSize] = useState<DealSize | "">("");
  const [confirmed, setConfirmed] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [successMessage, setSuccessMessage] = useState("");

  const selectedCustomer = demoCustomers.find(
    (customer) => customer.customerCode === customerCode,
  );

  const selectedProduct = demoProducts.find(
    (product) => product.productCode === productCode,
  );

  const quantityValue = Number(quantity);
  const sellingPriceValue = Number(sellingPrice);

  const preview =
    selectedProduct &&
    Number.isInteger(quantityValue) &&
    quantityValue > 0 &&
    Number.isFinite(sellingPriceValue) &&
    sellingPriceValue > 0
      ? calculateTransaction(selectedProduct, quantityValue, sellingPriceValue)
      : null;

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSuccessMessage("");

    const validationErrors = validateTransactionInput({
      customerCode,
      productCode,
      quantity: quantityValue,
      sellingPrice: sellingPriceValue,
      dealSize,
      confirmed,
    });

    if (!orderDate) {
      validationErrors.push("Please select an order date.");
    }

    if (
      validationErrors.length > 0 ||
      !selectedCustomer ||
      !selectedProduct ||
      !preview ||
      !dealSize
    ) {
      setErrors(validationErrors);
      return;
    }

    const transaction: Transaction = {
      transactionReference: `DEMO-${crypto.randomUUID()}`,

      customerCode: selectedCustomer.customerCode,
      customerName: selectedCustomer.customerName,

      productCode: selectedProduct.productCode,
      productName: selectedProduct.productName,

      orderDate,
      quantityOrdered: quantityValue,
      dealSize,

      ...preview,

      createdAt: new Date().toISOString(),
    };

    onSave(transaction);

    setErrors([]);
    setSuccessMessage("Demo transaction saved successfully.");
    setCustomerCode("");
    setProductCode("");
    setOrderDate(getLocalDate());
    setQuantity("1");
    setSellingPrice("");
    setDealSize("");
    setConfirmed(false);
  }

  return (
    <section className="transaction-form-section">
      <div className="transaction-form-heading">
        <div>
          <p className="section-eyebrow">TRANSACTION MANAGEMENT</p>
          <h2>New Transaction</h2>
          <p className="section-description">
            Enter transaction details. Calculations are generated automatically.
          </p>
        </div>
        <span className="demo-mode-tag">DEMO MODE</span>
      </div>

      <form onSubmit={handleSubmit} className="transaction-form">
        <div className="form-grid">
          <label className="form-field">
            <span>Customer</span>
            <select
              value={customerCode}
              onChange={(event) => setCustomerCode(event.target.value)}
            >
              <option value="">Select customer</option>
              {demoCustomers.map((customer) => (
                <option
                  key={customer.customerCode}
                  value={customer.customerCode}
                >
                  {customer.customerName}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Product</span>
            <select
              value={productCode}
              onChange={(event) => setProductCode(event.target.value)}
            >
              <option value="">Select product</option>
              {demoProducts.map((product) => (
                <option key={product.productCode} value={product.productCode}>
                  {product.productName}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Order Date</span>
            <input
              type="date"
              value={orderDate}
              onChange={(event) => setOrderDate(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Quantity Ordered</span>
            <input
              type="number"
              min="1"
              step="1"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Selling Price per Unit (USD)</span>
            <input
              type="number"
              min="0.01"
              step="0.01"
              placeholder="Enter selling price"
              value={sellingPrice}
              onChange={(event) => setSellingPrice(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Deal Size</span>
            <select
              value={dealSize}
              onChange={(event) =>
                setDealSize(event.target.value as DealSize | "")
              }
            >
              <option value="">Select deal size</option>
              <option value="Small">Small</option>
              <option value="Medium">Medium</option>
              <option value="Large">Large</option>
            </select>
          </label>
        </div>

        {selectedProduct && (
          <div className="product-info-panel">
            <div>
              <span>Product Category</span>
              <strong>{selectedProduct.productCategory}</strong>
            </div>
            <div>
              <span>Product MSRP</span>
              <strong>{formatCurrency(selectedProduct.msrp)}</strong>
            </div>
            <div>
              <span>Estimated Cost per Unit</span>
              <strong>{formatCurrency(selectedProduct.msrp * 0.5)}</strong>
            </div>
          </div>
        )}

        {preview && (
          <div className="calculation-panel">
            <h3>Calculation Preview</h3>
            <div className="calculation-grid">
              <div>
                <span>Total Sales</span>
                <strong>{formatCurrency(preview.sales)}</strong>
              </div>
              <div>
                <span>Profit per Unit</span>
                <strong>{formatCurrency(preview.profitPerUnit)}</strong>
              </div>
              <div>
                <span>Total Profit / Loss</span>
                <strong>{formatCurrency(preview.totalProfitLoss)}</strong>
              </div>
              <div>
                <span>Transaction Status</span>
                <strong
                  className={
                    preview.status === "Profit"
                      ? "status-profit"
                      : "status-loss"
                  }
                >
                  {preview.status}
                </strong>
              </div>
            </div>
          </div>
        )}

        <label className="confirmation-field">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
          />
          <span>
            I confirm that the transaction details entered above are correct.
          </span>
        </label>

        {errors.length > 0 && (
          <div className="form-alert form-alert-error" role="alert">
            <strong>Please review the following:</strong>
            <ul>
              {errors.map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          </div>
        )}

        {successMessage && (
          <div className="form-alert form-alert-success" role="status">
            {successMessage}
          </div>
        )}

        <button type="submit" className="save-transaction-button">
          Save Demo Transaction
        </button>

        <p className="form-disclaimer">
          Demo only. This transaction will not be submitted to Supabase or any
          production database.
        </p>
      </form>
    </section>
  );
}
