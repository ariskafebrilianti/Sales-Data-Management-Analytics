import { useMemo, useState } from "react";
import type { Transaction } from "../types/transaction";
import "./TransactionHistory.css";

interface TransactionHistoryProps {
  transactions: Transaction[];
  onClear: () => void;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(value);
}

function formatDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function TransactionHistory({
  transactions,
  onClear,
}: TransactionHistoryProps) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [dealSizeFilter, setDealSizeFilter] = useState("All");

  const filteredTransactions = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    return [...transactions]
      .filter((transaction) => {
        const matchesSearch =
          !keyword ||
          transaction.transactionReference.toLowerCase().includes(keyword) ||
          transaction.customerName.toLowerCase().includes(keyword) ||
          transaction.productName.toLowerCase().includes(keyword);

        const matchesStatus =
          statusFilter === "All" || transaction.status === statusFilter;

        const matchesDealSize =
          dealSizeFilter === "All" || transaction.dealSize === dealSizeFilter;

        return matchesSearch && matchesStatus && matchesDealSize;
      })
      .sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      );
  }, [transactions, search, statusFilter, dealSizeFilter]);

  function handleClear() {
    const confirmed = window.confirm(
      "Clear all demo transactions saved in this browser? This cannot be undone.",
    );

    if (confirmed) {
      onClear();
      setSearch("");
      setStatusFilter("All");
      setDealSizeFilter("All");
    }
  }

  return (
    <section className="history-section">
      <div className="history-heading">
        <div>
          <p className="section-eyebrow">TRANSACTION MANAGEMENT</p>
          <h2>Transaction History</h2>
          <p className="section-description">
            Review and search transactions saved in this browser.
          </p>
        </div>

        <button
          type="button"
          className="clear-demo-button"
          onClick={handleClear}
          disabled={transactions.length === 0}
        >
          Clear Demo Data
        </button>
      </div>

      <div className="history-summary">
        <div>
          <span>Total Transactions</span>
          <strong>{transactions.length}</strong>
        </div>
        <div>
          <span>Matching Transactions</span>
          <strong>{filteredTransactions.length}</strong>
        </div>
      </div>

      <div className="history-filters">
        <label className="history-search">
          <span>Search Transaction</span>
          <input
            type="search"
            placeholder="Search reference, customer, or product..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>

        <label>
          <span>Transaction Status</span>
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="All">All</option>
            <option value="Profit">Profit</option>
            <option value="Loss">Loss</option>
          </select>
        </label>

        <label>
          <span>Deal Size</span>
          <select
            value={dealSizeFilter}
            onChange={(event) => setDealSizeFilter(event.target.value)}
          >
            <option value="All">All</option>
            <option value="Small">Small</option>
            <option value="Medium">Medium</option>
            <option value="Large">Large</option>
          </select>
        </label>
      </div>

      <div className="history-table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>Transaction Reference</th>
              <th>Order Date</th>
              <th>Customer</th>
              <th>Product</th>
              <th>Quantity</th>
              <th>Deal Size</th>
              <th>Total Sales</th>
              <th>Total Profit / Loss</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {filteredTransactions.map((transaction) => (
              <tr key={transaction.transactionReference}>
                <td className="reference-cell">
                  {transaction.transactionReference}
                </td>
                <td>{formatDate(transaction.orderDate)}</td>
                <td>{transaction.customerName}</td>
                <td>{transaction.productName}</td>
                <td>{transaction.quantityOrdered}</td>
                <td>{transaction.dealSize}</td>
                <td>{formatCurrency(transaction.sales)}</td>
                <td>{formatCurrency(transaction.totalProfitLoss)}</td>
                <td>
                  <span
                    className={`history-status ${
                      transaction.status === "Profit"
                        ? "history-status-profit"
                        : "history-status-loss"
                    }`}
                  >
                    {transaction.status}
                  </span>
                </td>
              </tr>
            ))}

            {filteredTransactions.length === 0 && (
              <tr>
                <td colSpan={9} className="history-empty">
                  {transactions.length === 0
                    ? "No demo transactions saved yet."
                    : "No transactions match your search or filters."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <p className="history-disclaimer">
        Demo data is stored locally in this browser only. It is not connected to
        the production database.
      </p>
    </section>
  );
}
