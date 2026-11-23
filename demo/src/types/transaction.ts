
export type DealSize = "Small" | "Medium" | "Large";

export type TransactionStatus = "Profit" | "Loss";

export interface Customer {
  customerCode: string;
  customerName: string;
}

export interface Product {
  productCode: string;
  productName: string;
  productCategory: string;
  msrp: number;
}

export interface Transaction {
  transactionReference: string;

  customerCode: string;
  customerName: string;

  productCode: string;
  productName: string;

  orderDate: string;
  quantityOrdered: number;
  dealSize: DealSize;

  msrp: number;
  estimatedCostPerUnit: number;
  sellingPricePerUnit: number;

  sales: number;
  profitPerUnit: number;
  totalProfitLoss: number;
  status: TransactionStatus;

  createdAt: string;
}
