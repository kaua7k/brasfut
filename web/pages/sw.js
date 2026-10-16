// Service worker do BRASFUT no GitHub Pages (modelo: pages/montar.mjs troca a
// versao e a lista de arquivos a cada build).
//
// Na primeira visita guarda o app inteiro no aparelho - inclusive o Pyodide e
// os .py do motor, ~25 MB -, e dali em diante tudo sai do cache: o jogo abre
// sem internet. Build novo = versao nova = cache novo; o antigo e apagado
// quando o novo assume. O save nao mora aqui: fica no IndexedDB (worker do
// motor), que o service worker nunca toca.

const VERSAO = '__VERSAO__'
const CACHE = `brasfut-${VERSAO}`
const ARQUIVOS = [] /* __ARQUIVOS__ */

self.addEventListener('install', (ev) => {
  ev.waitUntil(
    caches
      .open(CACHE)
      .then((c) => c.addAll(ARQUIVOS))
      .then(() => self.skipWaiting()),
  )
})

self.addEventListener('activate', (ev) => {
  ev.waitUntil(
    caches
      .keys()
      .then((nomes) => Promise.all(nomes.filter((n) => n.startsWith('brasfut-') && n !== CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (ev) => {
  const req = ev.request
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return
  // abrir o app (ou recarregar em qualquer #tela) devolve o index guardado
  if (req.mode === 'navigate') {
    ev.respondWith(caches.match('./', { cacheName: CACHE }).then((r) => r || fetch(req)))
    return
  }
  // os .py vem com ?v=<hash do motor>: a chave do cache e o caminho
  ev.respondWith(
    caches.match(req, { cacheName: CACHE, ignoreSearch: true }).then((r) => r || fetch(req)),
  )
})
