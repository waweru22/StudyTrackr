import { defineConfig, loadEnv } from 'vite'
import type { Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Plugin to inject env vars into the Firebase service worker at build time.
// The public/firebase-messaging-sw.js file uses __VITE_FIREBASE_*__ placeholders
// which are replaced here, because service workers in /public cannot use import.meta.env.
function firebaseSwPlugin(env: Record<string, string>): Plugin {
  return {
    name: 'firebase-sw-env-inject',
    // Runs after the bundle is written, replacing the copied SW file
    closeBundle() {
      const swDist = path.resolve(__dirname, 'dist', 'firebase-messaging-sw.js')
      if (!fs.existsSync(swDist)) return
      let content = fs.readFileSync(swDist, 'utf-8')
      const vars = [
        'VITE_FIREBASE_API_KEY',
        'VITE_FIREBASE_AUTH_DOMAIN',
        'VITE_FIREBASE_PROJECT_ID',
        'VITE_FIREBASE_STORAGE_BUCKET',
        'VITE_FIREBASE_MESSAGING_SENDER_ID',
        'VITE_FIREBASE_APP_ID',
        'VITE_FIREBASE_MEASUREMENT_ID',
      ]
      for (const v of vars) {
        content = content.replaceAll(`__${v}__`, env[v] || '')
      }
      fs.writeFileSync(swDist, content, 'utf-8')
      console.log('[firebase-sw-env-inject] Service worker env vars injected.')
    },
    // Also serves the substituted SW during dev via a middleware
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url === '/firebase-messaging-sw.js') {
          const swSrc = path.resolve(__dirname, 'public', 'firebase-messaging-sw.js')
          let content = fs.readFileSync(swSrc, 'utf-8')
          const vars = [
            'VITE_FIREBASE_API_KEY',
            'VITE_FIREBASE_AUTH_DOMAIN',
            'VITE_FIREBASE_PROJECT_ID',
            'VITE_FIREBASE_STORAGE_BUCKET',
            'VITE_FIREBASE_MESSAGING_SENDER_ID',
            'VITE_FIREBASE_APP_ID',
            'VITE_FIREBASE_MEASUREMENT_ID',
          ]
          for (const v of vars) {
            content = content.replaceAll(`__${v}__`, env[v] || '')
          }
          res.setHeader('Content-Type', 'application/javascript')
          res.end(content)
          return
        }
        next()
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react(), firebaseSwPlugin(env)],
  }
})
