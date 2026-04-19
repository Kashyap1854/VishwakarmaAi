import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      "/api": {
        // In Docker, 'backend' is the service name. Outside Docker, localhost:5000 works.
        target: process.env.VITE_API_URL || "http://backend:5000",
        changeOrigin: true,
      },
    },
  },
});