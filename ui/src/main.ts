// ⛑ Dev-Guard: loggt & repariert HTTP-Calls zur API
if (import.meta.env.DEV) {
  // fetch
  const _fetch = window.fetch
  window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : (input as URL).toString()
    if (url.startsWith('http://api.workmate.test')) {
      console.warn('[https-guard][fetch] HTTP → HTTPS', url, '\n', new Error().stack)
      input = url.replace(/^http:\/\//, 'https://')
    }
    return _fetch(input as any, init)
  }

  // XMLHttpRequest
  const _open = XMLHttpRequest.prototype.open
  XMLHttpRequest.prototype.open = function (method: string, url: string, ...rest: any[]) {
    if (url.startsWith('http://api.workmate.test')) {
      console.warn('[https-guard][xhr] HTTP → HTTPS', url, '\n', new Error().stack)
      url = url.replace(/^http:\/\//, 'https://')
    }
    return _open.call(this, method, url, ...rest)
  }

  // axios (falls benutzt)
  // @ts-ignore
  if ((window as any).axios) {
    const ax = (window as any).axios
    try {
      const u = new URL(ax.defaults.baseURL || '', location.href)
      if (u.protocol === 'http:' && u.hostname === 'api.workmate.test') {
        u.protocol = 'https:'
        u.port = ''
        ax.defaults.baseURL = u.toString()
        console.warn('[https-guard][axios] baseURL →', ax.defaults.baseURL)
      }
    } catch {}
  }
}

import { createApp } from 'vue'
import App from './App.vue'
import './index.css'
import router from './router'
import './https-guard.dev'
import { initKeycloak } from './lib/keycloak'
import { useAuth } from './composables/useAuth'

const app = createApp(App)
app.use(router)

initKeycloak(async () => {
  const auth = useAuth()
  await auth.initAuth()
  console.log('🎉 Keycloak + useAuth initialisiert')
  app.mount('#app')
})
