import api from './index'

/** 我的报销单列表 */
export function getExpenses(params = {}) {
  return api.get('/expenses', { params })
}

/** 创建报销单 */
export function createExpense(data) {
  return api.post('/expenses', data)
}

/** 报销单详情 */
export function getExpense(id) {
  return api.get(`/expenses/${id}`)
}

/** 提交审批 */
export function submitExpense(id) {
  return api.post(`/expenses/${id}/submit`)
}

/** 上传发票附件 */
export function uploadAttachment(id, file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/expenses/${id}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
