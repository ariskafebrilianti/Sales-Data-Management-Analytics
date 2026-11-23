
import type { Customer, Product } from "../types/transaction";

export const demoCustomers: Customer[] = [
  {
    customerCode: "DEMO-C001",
    customerName: "Demo Customer Alpha",
  },
  {
    customerCode: "DEMO-C002",
    customerName: "Demo Customer Beta",
  },
  {
    customerCode: "DEMO-C003",
    customerName: "Demo Customer Gamma",
  },
  {
    customerCode: "DEMO-C004",
    customerName: "Demo Customer Delta",
  },
  {
    customerCode: "DEMO-C005",
    customerName: "Demo Customer Epsilon",
  },
];

export const demoProducts: Product[] = [
  {
    productCode: "DEMO-P001",
    productName: "Classic Car Model A",
    productCategory: "Classic Cars",
    msrp: 100,
  },
  {
    productCode: "DEMO-P002",
    productName: "Vintage Car Model B",
    productCategory: "Vintage Cars",
    msrp: 120,
  },
  {
    productCode: "DEMO-P003",
    productName: "Motorcycle Model C",
    productCategory: "Motorcycles",
    msrp: 80,
  },
  {
    productCode: "DEMO-P004",
    productName: "Aircraft Model D",
    productCategory: "Planes",
    msrp: 150,
  },
  {
    productCode: "DEMO-P005",
    productName: "Ship Model E",
    productCategory: "Ships",
    msrp: 90,
  },
  {
    productCode: "DEMO-P006",
    productName: "Train Model F",
    productCategory: "Trains",
    msrp: 75,
  },
  {
    productCode: "DEMO-P007",
    productName: "Truck Model G",
    productCategory: "Trucks and Buses",
    msrp: 110,
  },
];
