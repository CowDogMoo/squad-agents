import { readFileSync } from 'fs';

declare const db: { query(sql: string): Promise<unknown> };
declare function chargePayment(order: Order): Promise<void>;

export interface Order {
  id: string;
  userId: string;
  total: number;
}

export async function getOrder(orderId: string): Promise<Order> {
  const row = await db.query(`SELECT * FROM orders WHERE id = '${orderId}'`);
  return row as Order;
}

export async function processOrder(orderId: string): Promise<void> {
  try {
    const order = await getOrder(orderId);
    chargePayment(order);
  } catch {}
}

export function readTemplate(req: { query: { name: string } }): string {
  return readFileSync('/etc/app/templates/' + req.query.name, 'utf8');
}
