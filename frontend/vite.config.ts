import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0', // 允许从外部访问
    port: 5173,      // 明确指定前端开发服务器的端口
    // 关键修改：将所有 API 请求指向 Nginx 网关
    proxy: {
      '/api': {
        target: 'http://localhost:80', // 所有 /api 的请求都发往网关
        changeOrigin: true,
        // 不需要 rewrite，因为网关的 location 已经包含了 /api
      },
      '/media': {
        target: 'http://localhost:80', // 所有 /media 的请求也发往网关
        changeOrigin: true,
      }
    }
  },
})
