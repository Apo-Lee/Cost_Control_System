import api from './index'

/** 登录 — JSON 格式请求 */
export function login(username, password) {
  return api.post('/auth/login', { username, password })
}

/** 获取当前用户信息 */
export function getMe() {
  return api.get('/auth/me')
}
