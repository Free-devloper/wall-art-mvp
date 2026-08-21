import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { OrderStatusValue } from '../types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPrice(cents: number): string {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
  }).format(cents / 100);
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getStatusColor(status: OrderStatusValue | string): string {
  switch (status) {
    case 'new':
      return 'bg-yellow-100 text-yellow-800';
    case 'awaiting_approval':
      return 'bg-blue-100 text-blue-800';
    case 'paid':
      return 'bg-green-100 text-green-800';
    case 'in_production':
      return 'bg-indigo-100 text-indigo-800';
    case 'dispatched':
      return 'bg-teal-100 text-teal-800';
    case 'cancelled':
      return 'bg-red-100 text-red-800';
    case 'refunded':
      return 'bg-orange-100 text-orange-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function getStatusLabel(status: OrderStatusValue | string): string {
  const labels: Record<string, string> = {
    new: 'New',
    awaiting_approval: 'Awaiting Approval',
    paid: 'Paid',
    in_production: 'In Production',
    dispatched: 'Dispatched',
    cancelled: 'Cancelled',
    refunded: 'Refunded',
  };
  return labels[status] || status;
}
