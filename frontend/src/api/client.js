import axios from 'axios'

const localApiUrl = `${window.location.protocol}//${window.location.hostname}:8000`
const apiBaseUrl = import.meta.env.DEV
  ? localApiUrl
  : import.meta.env.VITE_API_BASE_URL || localApiUrl

const client = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export function errorMessage(error, fallback = '요청을 처리하지 못했습니다.') {
  return error.response?.data?.message || fallback
}

export default client
