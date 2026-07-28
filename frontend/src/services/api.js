import axios from 'axios'

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return ''
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(config => {
  config.headers['X-CSRFToken'] = getCookie('csrftoken')
  return config
})

api.interceptors.response.use(
  r => r,
  err => {
    // The session-check call is expected to 401 for logged-out users; let
    // AuthContext/PrivateRoute handle that via client-side routing instead
    // of forcing a hard reload here.
    const isSessionCheck = err.config?.url?.includes('/auth/session/')
    if (err.response?.status === 401 && !isSessionCheck && window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
