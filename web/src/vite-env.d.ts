/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 'navegador' no build do GitHub Pages: o motor roda num Web Worker (Pyodide). */
  readonly VITE_MODO?: string
}
