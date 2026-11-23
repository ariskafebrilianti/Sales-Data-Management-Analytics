import type { Transaction } from "../types/transaction";
import "./DashboardOverview.css";

interface DashboardOverviewProps {
  transactions: Transaction[];
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

export default function DashboardOverview({
  transactions,
}: DashboardOverviewProps) {
  const totalTransactions = transactions.length;

  const totalSales = transactions.reduce(
    (total, transaction) => total + transaction.sales,
    0,
  );

  const totalProfitLoss = transactions.reduce(
    (total, transaction) => total + transaction.totalProfitLoss,
    0,
  );

  const profitCount = transactions.filter(
    (transaction) => transaction.status === "Profit",
  ).length;

  const lossCount = transactions.filter(
    (transaction) => transaction.status === "Loss",
  ).length;

  const recentTransactions = [...transactions]
    .sort(
      (a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
    )
    .slice(0, 5);

  const kpis = [
    {
      label: "Total Transactions",
      value: totalTransactions.toLocaleString("en-US"),
      description: "Saved demo transactions",
    },
    {
      label: "Total Sales",
      value: formatCurrency(totalSales),
      description: "Combined transaction sales",
    },
    {
      label: "Total Profit / Loss",
      value: formatCurrency(totalProfitLoss),
      description: "Combined transaction result",
      valueClass: totalProfitLoss >= 0 ? "kpi-positive" : "kpi-negative",
    },
    {
      label: "Profit Transactions",
      value: profitCount.toLocaleString("en-US"),
      description: "Transactions with profit",
    },
    {
      label: "Loss Transactions",
      value: lossCount.toLocaleString("en-US"),
      description: "Transactions with loss",
    },
  ];

  return (
    <section className="dashboard-overview">
      <div className="dashboard-intro">
        <div>
          <p className="section-eyebrow">SALES MANAGEMENT SYSTEM</p>
          <h2>Welcome to Sales Analytics</h2>
          <p>
            Monitor transaction performance using data saved in this interactive
            demo.
          </p>
        </div>
        <span className="dashboard-demo-tag">LOCAL DEMO DATA</span>
      </div>

      <div className="kpi-grid">
        {kpis.map((kpi) => (
          <article className="kpi-card" key={kpi.label}>
            <span className="kpi-label">{kpi.label}</span>
            <strong className={kpi.valueClass ?? ""}>{kpi.value}</strong>
            <span className="kpi-description">{kpi.description}</span>
          </article>
        ))}
      </div>

      <section className="recent-transactions">
        <div className="recent-heading">
          <div>
            <h3>Recent Transactions</h3>
            <p>Latest transactions saved in this browser.</p>
          </div>
          <span>{recentTransactions.length} records</span>
        </div>

        {recentTransactions.length === 0 ? (
          <div className="dashboard-empty">
            <h4>No demo transactions yet</h4>
            <p>
              Add a transaction through the Transaction Input page to see
              dashboard metrics and recent activity.
            </p>
          </div>
        ) : (
          <div className="recent-table-wrapper">
            <table className="recent-table">
              <thead>
                <tr>
                  <th>Transaction Reference</th>
                  <th>Order Date</th>
                  <th>Customer</th>
                  <th>Product</th>
                  <th>Total Sales</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentTransactions.map((transaction) => (
                  <tr key={transaction.transactionReference}>
                    <td className="recent-reference">
                      {transaction.transactionReference}
                    </td>
                    <td>{formatDate(transaction.orderDate)}</td>
                    <td>{transaction.customerName}</td>
                    <td>{transaction.productName}</td>
                    <td>{formatCurrency(transaction.sales)}</td>
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
              </tbody>
            </table>
          </div>
        )}
      </section>

      <p className="dashboard-disclaimer">
        Metrics are calculated from demo transactions stored locally in this
        browser. They do not represent production database figures.
      </p>
    </section>
  );
}
