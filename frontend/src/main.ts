import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router' // 确保导入路由

// 导入Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
// 关键配置（顺序很重要！）
app.use(pinia)
app.use(router)   // 先注册路由
app.use(ElementPlus) // 再注册Element Plus

app.mount('#app')
