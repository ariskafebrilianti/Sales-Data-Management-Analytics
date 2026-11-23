
import type {
  DealSize,
  Product,
  Transaction,
  TransactionStatus,
} from "../types/transaction";

// Round to 2 decimal places using ROUND_HALF_UP
export function roundHalfUp(value: number): number {
  return Math.sign(value) *
    Math.round((Math.abs(value) + Number.EPSILON) * 100) / 100;
}

// Calculate transaction values
export function calculateTransaction(
  product: Product,
  quantity: number,
  sellingPrice: number,
): Pick<
  Transaction,
  | "msrp"
  | "estimatedCostPerUnit"
  | "sellingPricePerUnit"
  | "sales"
  | "profitPerUnit"
  | "totalProfitLoss"
  | "status"
> {
  const msrp = roundHalfUp(product.msrp);
  const estimatedCostPerUnit = roundHalfUp(msrp * 0.5);
  const sellingPricePerUnit = roundHalfUp(sellingPrice);

  const sales = roundHalfUp(sellingPricePerUnit * quantity);
  const profitPerUnit = roundHalfUp(
    sellingPricePerUnit - estimatedCostPerUnit,
  );
  const totalProfitLoss = roundHalfUp(profitPerUnit * quantity);

  const status: TransactionStatus =
    totalProfitLoss >= 0 ? "Profit" : "Loss";

  return {
    msrp,
    estimatedCostPerUnit,
    sellingPricePerUnit,
    sales,
    profitPerUnit,
    totalProfitLoss,
    status,
  };
}

// Validate transaction input
export function validateTransactionInput(input: {
  customerCode: string;
  productCode: string;
  quantity: number;
  sellingPrice: number;
  dealSize: DealSize | "";
  confirmed: boolean;
}): string[] {
  const errors: string[] = [];

  if (!input.customerCode) {
    errors.push("Please select a customer.");
  }

  if (!input.productCode) {
    errors.push("Please select a product.");
  }

  if (!Number.isInteger(input.quantity) || input.quantity < 1) {
    errors.push("Quantity must be a whole number greater than 0.");
  }

  if (!Number.isFinite(input.sellingPrice) || input.sellingPrice <= 0) {
    errors.push("Selling price must be greater than 0.");
  }

  if (!input.dealSize) {
    errors.push("Please select a deal size.");
  }

  if (!input.confirmed) {
    errors.push("Please confirm the transaction before saving.");
  }

  return errors;
}
