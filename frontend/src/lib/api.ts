import axios from 'axios';
import { getAuthHeader, removeToken } from './auth';
import type { Theme, Order, AdminOrder, CostReport } from '../types';

// Clerk token setter - called from components that have access to useAuth()
let clerkTokenGetter: (() => Promise<string | null>) | null = null;

export function setClerkTokenGetter(getter: () => Promise<string | null>) {
  clerkTokenGetter = getter;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use(async (config) => {
  // For customer API calls, attach Clerk token
  if (clerkTokenGetter && !config.url?.includes('/api/admin')) {
    try {
      const token = await clerkTokenGetter();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      // Silent fail - some routes don't require auth
    }
  }

  if (config.url?.startsWith('/api/admin')) {
    Object.assign(config.headers, getAuthHeader());
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && error.config.url?.startsWith('/api/admin')) {
      removeToken();
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

export const getThemes = () =>
  api.get<Theme[]>('/api/themes');

export const requestUploadUrl = (email: string, consent: boolean) =>
  api.post<{ upload_url: string; upload_id: string; fields: Record<string, string> }>(
    '/api/uploads',
    { customer_email: email, consent_confirmed: consent }
  );

export const createOrder = (data: {
  theme_id: string;
  upload_id: string;
  instructions?: string;
  product_size: string;
  customer_email: string;
  customer_name: string;
}) => api.post<Order>('/api/orders', data);

export const requestGeneration = (orderId: string, instructions?: string) =>
  api.post(`/api/orders/${orderId}/generate`, { instructions });

export const getGenerationStatus = (orderId: string) =>
  api.get<{ status: string; preview_url: string | null; remaining_regenerations: number }>(
    `/api/orders/${orderId}/generation-status`
  );

export const requestRegeneration = (orderId: string, reason?: string) =>
  api.post(`/api/orders/${orderId}/regenerate`, { reason });

export const approvePreview = (orderId: string) =>
  api.post(`/api/orders/${orderId}/approve`);

export const createCheckoutSession = (orderId: string) =>
  api.post<{ checkout_url: string }>(`/api/orders/${orderId}/checkout-session`);

export const getOrderConfirmation = (orderId: string) =>
  api.get<{ order_id: string; status: string; customer_email: string; total_cents: number }>(
    `/api/orders/${orderId}/confirmation`
  );

export const adminLogin = (email: string, password: string) =>
  api.post<{ token: string }>('/api/admin/auth/login', { email, password });

export const adminGetOrders = (page?: number, status?: string) =>
  api.get<{ items: AdminOrder[]; total: number; page: number; size: number }>('/api/admin/orders', { params: { page, status }, headers: getAuthHeader() });

export const adminGetOrder = (id: string) =>
  api.get<AdminOrder>(`/api/admin/orders/${id}`);

export const adminUpdateOrderStatus = (id: string, status: string, production_notes?: string) =>
  api.post(`/api/admin/orders/${id}/status`, { status, production_notes });

export const adminRegenerateOrder = (id: string) =>
  api.post(`/api/admin/orders/${id}/regenerate`);

export const adminGetProductionFile = (id: string) =>
  api.get<{ production_url: string }>(`/api/admin/orders/${id}/production-file`, { headers: getAuthHeader() });

export const adminDeletePhotos = (id: string) =>
  api.delete(`/api/admin/orders/${id}/photos`);

export const adminGetCosts = () =>
  api.get<CostReport>('/api/admin/costs');

export const adminGetThemes = () =>
  api.get<Theme[]>('/api/admin/themes');

export const adminCreateTheme = (data: Partial<Theme>) =>
  api.post<Theme>('/api/admin/themes', data);

export const adminUpdateTheme = (id: string, data: Partial<Theme>) =>
  api.patch<Theme>(`/api/admin/themes/${id}`, data);

export const adminDeleteTheme = (id: string) => api.delete(`/api/admin/themes/${id}`, { headers: getAuthHeader() });

export default api;
