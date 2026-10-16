import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

// O build vai para web/dist, que e exatamente a pasta que o server.py serve.
// Em desenvolvimento o Vite fica no 5173 e manda /api para o Python no 8770,
// entao o mesmo codigo roda nos dois modos sem if de ambiente.
//
// `--mode pages` (npm run build:pages) e a versao do celular para o GitHub
// Pages: caminhos relativos (o site mora em /<repo>/), saida em
// web/dist-pages, VITE_MODO=navegador (o motor roda num Web Worker com
// Pyodide) e o index com manifesto e icones da PWA. O resto - o
// Pyodide, os .py e o service worker - entra depois, em pages/montar.mjs.

function htmlDaPwa(): Plugin {
  const cabeca = [
    '<link rel="manifest" href="manifest.webmanifest" />',
    '<link rel="icon" href="icones/icone.svg" type="image/svg+xml" />',
    '<link rel="apple-touch-icon" href="icones/icone-180.png" />',
    '<meta name="theme-color" content="#0b0c0e" />',
    '<meta name="mobile-web-app-capable" content="yes" />',
    '<meta name="apple-mobile-web-app-capable" content="yes" />',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black" />',
    '<meta name="apple-mobile-web-app-title" content="BRASFUT" />',
  ].join('\n    ')
  return {
    name: 'brasfut-pwa',
    transformIndexHtml: (html) => html.replace('</head>', `  ${cabeca}\n  </head>`),
  }
}

// No build normal o cliente do worker vira um modulo vazio: o Rollup le os
// import() mesmo nos ramos mortos, e sem isto o worker do Pyodide sairia como
// arquivo orfao em web/dist.
function semMotorNoNavegador(): Plugin {
  const vazio = '\0brasfut-sem-motor'
  return {
    name: 'brasfut-sem-motor',
    enforce: 'pre',
    resolveId: (id) => (/[/\\]motor[/\\]cliente(\.ts)?$/.test(id) ? vazio : null),
    load: (id) =>
      id === vazio
        ? 'const f = () => { throw new Error("modo navegador desligado neste build") }\n' +
          'export const aoProgresso = f, iniciarMotor = f, pedirAoMotor = f, medirDesempenho = f'
        : null,
  }
}

export default defineConfig(({ mode }) => {
  const pages = mode === 'pages'
  return {
    base: pages ? './' : '/',
    plugins: pages ? [react(), htmlDaPwa()] : [react(), semMotorNoNavegador()],
    build: { outDir: pages ? 'dist-pages' : 'dist', emptyOutDir: true },
    // trocado no texto (e nao lido do .env) para o build normal dobrar
    // `MODO_NAVEGADOR` em false e deixar o worker e o Pyodide fora do web/dist
    define: { 'import.meta.env.VITE_MODO': JSON.stringify(pages ? 'navegador' : '') },
    worker: { format: 'es' },
    server: {
      port: 5173,
      proxy: { '/api': { target: 'http://127.0.0.1:8770', changeOrigin: false } },
    },
  }
})
