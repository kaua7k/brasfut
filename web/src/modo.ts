// Onde o motor roda. No build normal (web/dist, servido pelo server.py) ha um
// servidor Python e o front fala com ele por HTTP. No build do GitHub Pages
// (npm run build:pages, versao do celular) nao ha servidor: o motor roda no
// proprio navegador, num Web Worker com Pyodide (src/motor/).
//
// A constante e trocada no build: no build normal o ramo do worker some do
// bundle.
export const MODO_NAVEGADOR = import.meta.env.VITE_MODO === 'navegador'
