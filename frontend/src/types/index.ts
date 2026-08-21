// Types matching backend Pydantic schema responses (snake_case from FastAPI)

export interface Theme {
  id: string;
  name: string;
  description: string;
  prompt_template: string;
  example_image_url?: string;
  price_cents: number;
  max_regenerations: number;
  sort_order: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export type OrderStatusValue =
  | 'new'
  | 'awaiting_approval'
  | 'paid'
  | 'in_production'
  | 'dispatched'
  | 'cancelled'
  | 'refunded';

export interface Order {
  id: string;
  status: OrderStatusValue;
  theme_id: string;
  product_size: string;
  price_cents: number;
  customer_email: string;
  customer_name?: string;
  stripe_payment_id?: string;
  stripe_checkout_session_id?: string;
  shipping_address_line1?: string;
  shipping_address_line2?: string;
  shipping_city?: string;
  shipping_postcode?: string;
  shipping_country?: string;
  created_at: string;
  updated_at: string;
}

export interface Generation {
  id: string;
  order_id: string;
  status: string;
  preview_url?: string;
  cost_usd?: number;
  generation_time_ms?: number;
  created_at: string;
  completed_at?: string;
  failure_reason?: string;
}

export interface AdminOrder extends Order {
  generations?: Generation[];
  upload_url?: string;
  payment_status?: string;
}

export interface CostReport {
  total_today: number;
  total_this_week?: number;
  total_this_month: number;
  average_cost: number;
  cost_by_theme?: Record<string, number>;
  per_theme?: Record<string, number>;
  daily_spend: Array<{ date: string; amount?: number; total?: number }>;
  daily_cap?: number;
  monthly_cap?: number;
}

export interface ProductSize {
  id: string;
  name: string;
  dimensions: string;
  price_cents: number;
}

export const PRODUCT_SIZES: ProductSize[] = [
  { id: 'A3', name: 'Small (A3)', dimensions: '30 × 42 cm', price_cents: 2999 },
  { id: 'A2', name: 'Medium (A2)', dimensions: '42 × 59 cm', price_cents: 4999 },
  { id: 'A1', name: 'Large (A1)', dimensions: '59 × 84 cm', price_cents: 7999 },
  { id: 'A0', name: 'Extra Large (A0)', dimensions: '84 × 119 cm', price_cents: 11999 },
];
