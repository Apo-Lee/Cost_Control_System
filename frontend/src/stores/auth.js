import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  // ===== 状态 =====
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // ===== 计算属性 =====
  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')

  // ===== 方法 =====

  /** 登录 */
  async function loginAction(username, password) {
    const res = await loginApi(username, password)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)

    // 获取用户信息
    const userInfo = await getMe()
    user.value = userInfo
    localStorage.setItem('user', JSON.stringify(userInfo))
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isLoggedIn, userRole, loginAction, logout }
})
