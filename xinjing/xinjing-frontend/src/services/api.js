const BASE = '/api/v1'

function getToken() {
  try {
    return JSON.parse(localStorage.getItem('xinjing_auth') || 'null')?.token ?? null
  } catch {
    return null
  }
}

async function request(method, path, body) {
  const token = getToken()
  const isFormData = body instanceof FormData
  const headers = {}
  if (!isFormData) headers['Content-Type'] = 'application/json'  // FormData 让浏览器自动带 boundary
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? (isFormData ? body : JSON.stringify(body)) : undefined,
    })

    if (!res.ok) {
      // token 过期或无效，清除登录态并跳转到登录页
      if (res.status === 401) {
        localStorage.removeItem('xinjing_auth')
        window.location.href = '/login'
        throw new Error('Unauthorized')
      }
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }

    if (res.status === 204) return null
    return res.json()
  } catch (error) {
    // 网络错误或其他fetch错误
    if (error.name === 'TypeError' || error.message.includes('fetch')) {
      throw new Error('网络连接失败，请检查网络状态')
    }
    throw error
  }
}

export const api = {
  get:    (path)       => request('GET',    path),
  post:   (path, body) => request('POST',   path, body),
  put:    (path, body) => request('PUT',    path, body),
  patch:  (path, body) => request('PATCH',  path, body),
  delete: (path)       => request('DELETE', path),
}
