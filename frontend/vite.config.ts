import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

/**
 * Django сервира build-а през django-vite. Затова:
 *  - `outDir` сочи в staticfiles директорията на Django, а не в dist/;
 *  - `manifest` е задължителен — django-vite чете от него хешираните имена;
 *  - НЯМА index.html: entry point-овете са именувани и се вмъкват в
 *    Django template чрез {% vite_asset %}.
 */
export default defineConfig({
  plugins: [react()],
  base: "/static/",
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  build: {
    manifest: "manifest.json",
    outDir: path.resolve(__dirname, "../static/dist"),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        apply: path.resolve(__dirname, "src/entries/apply.tsx"),
      },
    },
  },
  server: {
    port: 5173,
    origin: "http://localhost:5173",
    // Django dev сървърът вика Vite от друг порт.
    cors: true,
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    globals: true,
  },
});
