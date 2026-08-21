import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    watch: {
      // Use polling for Docker on Windows/WSL2 — native fs events
      // don't propagate through the Docker volume mount
      usePolling: true,
      interval: 1000,
    },
    hmr: {
      // HMR connects from the browser on the host
      host: 'localhost',
      port: 5173,
    },
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
});
