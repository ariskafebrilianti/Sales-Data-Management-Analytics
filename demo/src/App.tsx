import { useState } from "react";
import "./App.css";

import TransactionForm from "./components/TransactionForm";
import TransactionHistory from "./components/TransactionHistory";
import DashboardOverview from "./components/DashboardOverview";
import ReferenceData from "./components/ReferenceData";
import { demoCustomers, demoProducts } from "./data/demoData";
import type { Transaction } from "./types/transaction";

type Page =
  | "Dashboard Overview"
  | "Transaction Input"
  | "Transaction History"
  | "Reference Data";

const STORAGE_KEY = "sales-analytics-demo-transactions-v1";

const navigation = [
  { name: "Dashboard Overview", icon: "▦" },
  { name: "Transaction Input", icon: "＋" },
  { name: "Transaction History", icon: "◷" },
  { name: "Reference Data", icon: "▤" },
] as const;

function loadDemoTransactions(): Transaction[] {
  try {
    const storedData = localStorage.getItem(STORAGE_KEY);

    if (!storedData) {
      return [];
    }

    const parsedData: unknown = JSON.parse(storedData);

    return Array.isArray(parsedData) ? (parsedData as Transaction[]) : [];
  } catch {
    return [];
  }
}

function App() {
  const [activePage, setActivePage] = useState<Page>("Dashboard Overview");

  const [transactions, setTransactions] =
    useState<Transaction[]>(loadDemoTransactions);

  function handleClearTransactions() {
    localStorage.removeItem(STORAGE_KEY);
    setTransactions([]);
  }

  function handleSaveTransaction(transaction: Transaction) {
    setTransactions((currentTransactions) => {
      const updatedTransactions = [transaction, ...currentTransactions];

      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedTransactions));
      } catch (error) {
        console.error("Unable to save demo transaction:", error);
      }

      return updatedTransactions;
    });
  }

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div>
            <h2>Sales Analytics</h2>
            <span>Management System</span>
          </div>
        </div>

        <div className="demo-label">
          <span className="status-dot" />
          DEMO MODE
        </div>

        <div className="nav-section">
          <p className="nav-heading">WORKSPACE</p>

          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? "active" : ""}`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="user-avatar">DA</div>
          <div>
            <strong>Demo Account</strong>
            <span>Guest Access</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace / </span>
            <strong>{activePage}</strong>
          </div>

          <span className="demo-badge">Interactive Demo</span>
        </header>

        <section className="page-content">
          {activePage !== "Transaction Input" &&
            activePage !== "Transaction History" &&
            activePage !== "Reference Data" && (
              <div className="page-heading">
                <div>
                  <h1>{activePage}</h1>
                  <p>
                    Monitor and manage your sales transactions through a
                    structured data system.
                  </p>
                </div>
              </div>
            )}

          {activePage === "Dashboard Overview" && (
            <DashboardOverview transactions={transactions} />
          )}

          {activePage === "Transaction Input" && (
            <TransactionForm onSave={handleSaveTransaction} />
          )}

          {activePage === "Transaction History" && (
            <TransactionHistory
              transactions={transactions}
              onClear={handleClearTransactions}
            />
          )}

          {activePage === "Reference Data" && (
            <ReferenceData customers={demoCustomers} products={demoProducts} />
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
