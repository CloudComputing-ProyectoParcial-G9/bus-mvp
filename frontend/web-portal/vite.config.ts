import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    host: '0.0.0.0', // permite conexiones externas
    port: 5173,
    allowedHosts: [
      'lb-prod-308585431.us-east-1.elb.amazonaws.com', // Load Balancer DNS
      '54.161.1.30',    // Máquina de Producción 1
      '52.200.140.111', // Máquina de Producción 2
      '52.73.204.244'   // Máquina de Ingesta
    ]
  }
});
