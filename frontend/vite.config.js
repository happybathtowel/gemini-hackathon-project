import path from "path";
import { fileURLToPath } from "url";
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// https://vite.dev/config/
// Config updated to force restart (attempt 8)
export default defineConfig({
  plugins: [svelte()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "$lib": path.resolve(__dirname, "./src/lib"),
    },
  },
})
