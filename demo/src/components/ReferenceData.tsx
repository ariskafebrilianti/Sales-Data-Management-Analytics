import type { Customer, Product, DealSize } from "../types/transaction";
import "./ReferenceData.css";

interface ReferenceDataProps {
  customers: Customer[];
  products: Product[];
}

const dealSizes: DealSize[] = ["Small", "Medium", "Large"];

export default function ReferenceData({
  customers,
  products,
}: ReferenceDataProps) {
  const productCategories = [
    ...new Set(products.map((product) => product.productCategory)),
  ].sort();

  const summary = [
    { label: "Total Customers", value: customers.length },
    { label: "Total Products", value: products.length },
    { label: "Product Categories", value: productCategories.length },
  ];

  return (
    <section className="reference-data">
      <div className="reference-intro">
        <div>
          <p className="reference-eyebrow">MASTER DATA</p>
          <h2>Reference Data</h2>
          <p>
            Browse the customer, product, and deal size references used in this
            interactive demo.
          </p>
        </div>
        <span className="reference-demo-tag">DEMO DATA</span>
      </div>

      <div className="reference-summary">
        {summary.map((item) => (
          <article className="reference-summary-card" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>

      <section className="reference-panel">
        <div className="reference-panel-heading">
          <div>
            <h3>Customer Reference</h3>
            <p>Available demo customers for transaction input.</p>
          </div>
          <span>{customers.length} records</span>
        </div>

        <div className="reference-table-wrapper">
          <table className="reference-table">
            <thead>
              <tr>
                <th>Customer Code</th>
                <th>Customer Name</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.customerCode}>
                  <td className="reference-code">{customer.customerCode}</td>
                  <td>{customer.customerName}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="reference-panel">
        <div className="reference-panel-heading">
          <div>
            <h3>Product Reference</h3>
            <p>Available demo products and their reference prices.</p>
          </div>
          <span>{products.length} records</span>
        </div>

        <div className="reference-table-wrapper">
          <table className="reference-table">
            <thead>
              <tr>
                <th>Product Code</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>MSRP (USD)</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.productCode}>
                  <td className="reference-code">{product.productCode}</td>
                  <td>{product.productName}</td>
                  <td>{product.productCategory}</td>
                  <td>
                    {product.msrp.toLocaleString("en-US", {
                      style: "currency",
                      currency: "USD",
                    })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="reference-panel">
        <div className="reference-panel-heading">
          <div>
            <h3>Deal Size Options</h3>
            <p>Available deal size classifications for demo transactions.</p>
          </div>
          <span>{dealSizes.length} options</span>
        </div>

        <div className="deal-size-list">
          {dealSizes.map((size) => (
            <span className="deal-size-item" key={size}>
              {size}
            </span>
          ))}
        </div>
      </section>

      <p className="reference-disclaimer">
        Reference records are synthetic demo data. They are not connected to the
        production database.
      </p>
    </section>
  );
}
