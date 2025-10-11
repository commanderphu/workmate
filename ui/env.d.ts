/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  // hier kannst du weitere ENV-Variablen ergänzen
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
