import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export function errorMessage(error, fallback = '요청을 처리하지 못했습니다.') {
  return error.response?.data?.message || fallback
}

export default client

