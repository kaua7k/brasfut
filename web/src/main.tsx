import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'
import { MODO_NAVEGADOR } from './modo'
import './estilo/base.css'

const raiz = document.getElementById('raiz')
if (!raiz) throw new Error('faltou a div#raiz no index.html')

// versao do celular (GitHub Pages): o service worker guarda o app e o Python
// no aparelho, e o jogo passa a abrir sem internet (pages/sw.js)
if (MODO_NAVEGADOR && import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch((e) => console.warn('BRASFUT: service worker', e))
  })
}

createRoot(raiz).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
