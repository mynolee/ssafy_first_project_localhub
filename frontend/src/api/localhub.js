import client from './client'

export const placesApi = {
  async list(category) {
    const response = await client.get('/api/places', { params: category ? { category } : {} })
    return response.data.data
  },
}

export const postsApi = {
  async list(category) {
    const response = await client.get('/api/posts', { params: category ? { category } : {} })
    return response.data.data
  },
  async get(id) {
    const response = await client.get(`/api/posts/${id}`)
    return response.data.data
  },
  async create(payload) {
    const response = await client.post('/api/posts', payload)
    return response.data.data
  },
  async update(id, payload) {
    const response = await client.patch(`/api/posts/${id}`, payload)
    return response.data.data
  },
  async remove(id, password) {
    const response = await client.delete(`/api/posts/${id}`, { data: { password } })
    return response.data.data
  },
}

export const chatApi = {
  async send(message, history) {
    const response = await client.post('/api/chat', { message, history })
    return response.data.data
  },
}

