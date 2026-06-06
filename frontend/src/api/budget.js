import api from './index'

/** 预算列表 */
export function getBudgets(params = {}) {
  return api.get('/budgets', { params })
}

/** 创建预算 */
export function createBudget(data) {
  return api.post('/budgets', data)
}

/** 预算详情 */
export function getBudget(id) {
  return api.get(`/budgets/${id}`)
}

/** 提交审批 */
export function submitBudget(id) {
  return api.post(`/budgets/${id}/submit`)
}

/** 预算调整 */
export function adjustBudget(id, data) {
  return api.post(`/budgets/${id}/adjust`, data)
}

/** 预算预警 */
export function getBudgetAlerts(threshold = 0.8) {
  return api.get('/budgets/alerts/list', { params: { threshold } })
}
