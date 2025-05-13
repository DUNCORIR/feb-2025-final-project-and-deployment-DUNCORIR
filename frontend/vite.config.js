import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: process.env.NODE_ENV === "production" ? "/Gaine_Africa_app/" : "/",
  plugins: [react()],
  build: {
    outDir: "dist",
  },
});
