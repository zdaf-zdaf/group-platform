import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
})

//请求拦截器
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

//响应拦截器
instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || error.message
    return Promise.reject(message)
  },
)

export default instance
