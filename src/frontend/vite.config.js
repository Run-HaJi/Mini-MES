import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // 👇 重点是加上这一段！
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 后端地址
        changeOrigin: true, // 允许跨域
        // rewrite: (path) => path.replace(/^\/api/, '') // 注意：我们的后端路由本身就有 /api，所以这里不需要 rewrite 去掉它！
      }
    }
  }
})