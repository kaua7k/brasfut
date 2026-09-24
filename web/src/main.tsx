import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'
import './estilo/base.css'

const raiz = document.getElementById('raiz')
if (!raiz) throw new Error('faltou a div#raiz no index.html')

createRoot(raiz).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
