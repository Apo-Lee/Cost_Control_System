<template>
  <div class="approval-page">
    <h2>审批中心</h2>

    <el-tabs v-model="activeTab" @tab-change="fetchPending">
      <el-tab-pane label="待审批" name="pending">
        <el-table :data="pendingItems" v-loading="loading" stripe>
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.target_type === 'expense_report' ? 'primary' : 'warning'" size="small">
                {{ row.target_type === 'expense_report' ? '报销单' : '预算' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column label="金额" width="140">
            <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="提交时间" width="170">
            <template #default="{ row }">
              {{ row.submitted_at ? new Date(row.submitted_at).toLocaleString('zh-CN') : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="300" fixed="right">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleApprove(row)">
                <el-icon><Select /></el-icon>
                通过
              </el-button>
              <el-button type="danger" size="small" @click="handleReject(row)">
                <el-icon><CloseBold /></el-icon>
                驳回
              </el-button>
              <el-button size="small" @click="viewHistory(row)">历史</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && pendingItems.length === 0" description="暂无待审批项" />
      </el-tab-pane>
    </el-tabs>

    <!-- 审批意见弹窗 -->
    <el-dialog v-model="showActionDialog" :title="actionTitle" width="450px">
      <el-form>
        <el-form-item label="审批意见">
          <el-input
            v-model="comment"
            type="textarea"
            :rows="3"
            placeholder="选填"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showActionDialog = false">取消</el-button>
        <el-button :type="actionType === 'approved' ? 'success' : 'danger'" :loading="acting" @click="doAction">
          确认{{ actionType === 'approved' ? '通过' : '驳回' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 审批历史弹窗 -->
    <el-dialog v-model="showHistoryDialog" title="审批历史" width="550px">
      <el-timeline v-if="history.length > 0">
        <el-timeline-item
          v-for="item in history"
          :key="item.id"
          :type="item.action === 'approved' ? 'success' : 'danger'"
          :timestamp="new Date(item.created_at).toLocaleString('zh-CN')"
        >
          <strong>{{ item.action === 'approved' ? '✅ 通过' : '❌ 驳回' }}</strong>
          <span style="margin-left: 8px; color: #909399">审批人 ID: {{ item.approver_id }}</span>
          <div v-if="item.comment" style="color: #606266; margin-top: 4px">{{ item.comment }}</div>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无审批记录" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Select, CloseBold } from '@element-plus/icons-vue'
import api from '../../api/index'

const activeTab = ref('pending')
const loading = ref(false)
const acting = ref(false)
const pendingItems = ref([])
const showActionDialog = ref(false)
const showHistoryDialog = ref(false)
const history = ref([])
const comment = ref('')
const actionType = ref('approved')
const currentItem = ref(null)
const actionTitle = ref('')

function formatType(type) {
  return type === 'expense_report' ? '报销单' : '预算'
}

async function fetchPending() {
  loading.value = true
  try {
    pendingItems.value = await api.get('/approvals/pending')
  } finally {
    loading.value = false
  }
}

function handleApprove(row) {
  currentItem.value = row
  actionType.value = 'approved'
  actionTitle.value = `通过 ${formatType(row.target_type)} — ${row.title}`
  comment.value = ''
  showActionDialog.value = true
}

function handleReject(row) {
  currentItem.value = row
  actionType.value = 'rejected'
  actionTitle.value = `驳回 ${formatType(row.target_type)} — ${row.title}`
  comment.value = ''
  showActionDialog.value = true
}

async function doAction() {
  acting.value = true
  try {
    await api.post(
      `/approvals/${currentItem.value.target_type}/${currentItem.value.target_id}/approve`,
      { action: actionType.value, comment: comment.value || null }
    )
    ElMessage.success(actionType.value === 'approved' ? '已通过' : '已驳回')
    showActionDialog.value = false
    fetchPending()
  } finally {
    acting.value = false
  }
}

async function viewHistory(row) {
  try {
    history.value = await api.get(`/approvals/history/${row.target_type}/${row.target_id}`)
    showHistoryDialog.value = true
  } catch {}
}

onMounted(fetchPending)
</script>
