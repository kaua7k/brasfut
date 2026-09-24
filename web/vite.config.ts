import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// O build vai para web/dist, que e exatamente a pasta que o server.py serve.
// Em desenvolvimento o Vite fica no 5173 e manda /api para o Python no 8770,
// entao o mesmo codigo roda nos dois modos sem if de ambiente.
export default defineConfig({
  plugins: [react()],
  build: { outDir: 'dist', emptyOutDir: true },
  server: {
    port: 5173,
    proxy: { '/api': { target: 'http://127.0.0.1:8770', changeOrigin: false } },
  },
})
