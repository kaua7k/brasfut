// Segunda metade do `npm run build:pages` (a primeira e o `vite build --mode
// pages`, que gera o app em web/dist-pages). Aqui entra o que faz o app
// funcionar sem servidor e sem internet:
//
//   pyodide/            o Python em WebAssembly (do pacote npm `pyodide`,
//                       versao exata no package.json): servido junto, sem CDN
//   motor/py/           os .py do jogo (brasfut.py, dados_*.py, api/)
//   motor/arquivos.json a lista deles e um hash, que o worker usa para baixar
//   manifest.webmanifest + icones/   o que torna o site instalavel (PWA)
//   sw.js               service worker: guarda tudo isso no aparelho na
//                       primeira visita; depois o jogo abre offline
//   .nojekyll           o GitHub Pages nao esconde api/__init__.py
//
// Node puro, sem dependencia: roda igual no CI e na maquina de quem mexe.

import { createHash } from 'node:crypto'
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const WEB = dirname(dirname(fileURLToPath(import.meta.url)))
const RAIZ = dirname(WEB)
const SAIDA = join(WEB, 'dist-pages')

const PYODIDE = ['pyodide.mjs', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']
const CORES = { fundo: '#0b0c0e', tema: '#0b0c0e' }

if (!existsSync(join(SAIDA, 'index.html'))) {
  console.error('falta web/dist-pages: rode antes `vite build --mode pages`')
  process.exit(1)
}

function copiar(de, para) {
  mkdirSync(dirname(para), { recursive: true })
  copyFileSync(de, para)
}

function hash(dados) {
  return createHash('sha256').update(dados).digest('hex').slice(0, 12)
}

// ------------------------------------------------------------------ pyodide
const origemPyodide = join(WEB, 'node_modules', 'pyodide')
for (const arq of PYODIDE) copiar(join(origemPyodide, arq), join(SAIDA, 'pyodide', arq))
const versaoPyodide = JSON.parse(readFileSync(join(origemPyodide, 'package.json'), 'utf8')).version

// ---------------------------------------------------------------- motor .py
const arquivos = ['brasfut.py', 'dados_mundo.py', 'dados_clubes.py']
for (const arq of readdirSync(join(RAIZ, 'api')).sort()) if (arq.endsWith('.py')) arquivos.push(`api/${arq}`)
const h = createHash('sha256')
for (const arq of arquivos) {
  const dados = readFileSync(join(RAIZ, arq))
  h.update(arq).update(dados)
  copiar(join(RAIZ, arq), join(SAIDA, 'motor', 'py', arq))
}
const versaoMotor = h.digest('hex').slice(0, 12)
writeFileSync(join(SAIDA, 'motor', 'arquivos.json'), JSON.stringify({ versao: versaoMotor, arquivos }, null, 1))

// --------------------------------------------------------------------- PWA
for (const arq of readdirSync(join(WEB, 'pages', 'icones'))) copiar(join(WEB, 'pages', 'icones', arq), join(SAIDA, 'icones', arq))
const manifesto = {
  name: 'BRASFUT',
  short_name: 'BRASFUT',
  description: 'Carreira de tecnico no futebol brasileiro. Roda no aparelho, sem servidor, e funciona offline.',
  lang: 'pt-BR',
  start_url: './',
  scope: './',
  display: 'standalone',
  background_color: CORES.fundo,
  theme_color: CORES.tema,
  icons: [
    { src: 'icones/icone-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
    { src: 'icones/icone-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
    { src: 'icones/icone-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
    { src: 'icones/icone.svg', sizes: 'any', type: 'image/svg+xml' },
  ],
}
writeFileSync(join(SAIDA, 'manifest.webmanifest'), JSON.stringify(manifesto, null, 1))
writeFileSync(join(SAIDA, '.nojekyll'), '')

// ----------------------------------------------------------- service worker
function listar(pasta) {
  const fora = []
  for (const nome of readdirSync(pasta)) {
    const caminho = join(pasta, nome)
    if (statSync(caminho).isDirectory()) fora.push(...listar(caminho))
    else fora.push(caminho)
  }
  return fora
}
const guardar = listar(SAIDA)
  .map((c) => relative(SAIDA, c).split(sep).join('/'))
  .filter((c) => c !== 'sw.js' && c !== '.nojekyll' && !c.endsWith('.map'))
  .sort()
const versaoApp = hash(guardar.map((c) => c + hash(readFileSync(join(SAIDA, c)))).join('\n'))
const sw = readFileSync(join(WEB, 'pages', 'sw.js'), 'utf8')
  .replace("'__VERSAO__'", JSON.stringify(versaoApp))
  .replace('[] /* __ARQUIVOS__ */', JSON.stringify(['./', ...guardar.filter((c) => c !== 'index.html')], null, 1))
writeFileSync(join(SAIDA, 'sw.js'), sw)

const mb = guardar.reduce((s, c) => s + statSync(join(SAIDA, c)).size, 0) / 1048576
console.log(
  `dist-pages: pyodide ${versaoPyodide}, motor ${versaoMotor} (${arquivos.length} .py), ` +
    `service worker ${versaoApp} com ${guardar.length} arquivos (${mb.toFixed(1)} MB)`,
)
