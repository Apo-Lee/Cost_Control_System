<template>
  <div class="budget-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <h2>预算管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增预算
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="年度">
          <el-select v-model="filters.year" clearable placeholder="全部" style="width: 120px">
            <el-option v-for="y in years" :key="y" :label="y" :value="y" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部" style="width: 120px">
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已审批" value="approved" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchBudgets">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预算列表 -->
    <el-card>
      <el-table :data="budgets" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column prop="quarter" label="季度" width="80">
          <template #default="{ row }">
            {{ row.quarter ? `Q${row.quarter}` : '全年' }}
          </template>
        </el-table-column>
        <el-table-column prop="department_id" label="部门ID" width="80" />
        <el-table-column prop="expense_type_id" label="费用类型ID" width="100" />
        <el-table-column label="预算金额" width="140">
          <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="已使用" width="140">
          <template #default="{ row }">¥{{ row.used_amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="执行进度" min-width="180">
          <template #default="{ row }">
            <el-progress
              :percentage="usagePercent(row)"
              :color="progressColor(row)"
              :stroke-width="18"
            >
              <span>{{ usagePercent(row) }}%</span>
            </el-progress>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'draft'"
              type="success"
              size="small"
              @click="handleSubmit(row.id)"
            >
              提交
            </el-button>
            <el-button size="small" @click="openAdjust(row)">调整</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增预算弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新增预算" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="部门ID">
          <el-input-number v-model="form.department_id" :min="1" />
        </el-form-item>
        <el-form-item label="费用类型ID">
          <el-input-number v-model="form.expense_type_id" :min="1" />
        </el-form-item>
        <el-form-item label="年度">
          <el-input-number v-model="form.year" :min="2024" :max="2099" />
        </el-form-item>
        <el-form-item label="季度">
          <el-select v-model="form.quarter" clearable placeholder="全年">
            <el-option :value="1" label="Q1" />
            <el-option :value="2" label="Q2" />
            <el-option :value="3" label="Q3" />
            <el-option :value="4" label="Q4" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算金额">
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" :step="1000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- 预算调整弹窗 -->
    <el-dialog v-model="showAdjustDialog" title="预算调整" width="500px">
      <el-form :model="adjustForm" label-width="100px">
        <el-form-item label="调整金额">
          <el-input-number v-model="adjustForm.adjustment_amount" :precision="2" :step="1000" />
          <span class="form-hint">正数追加，负数调减</span>
        </el-form-item>
        <el-form-item label="调整原因">
          <el-input v-model="adjustForm.reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdjustDialog = false">取消</el-button>
        <el-button type="primary" :loading="adjusting" @click="handleAdjust">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getBudgets, createBudget, submitBudget, adjustBudget } from '../../api/budget'

const loading = ref(false)
const creating = ref(false)
const adjusting = ref(false)
const budgets = ref([])
const showCreateDialog = ref(false)
const showAdjustDialog = ref(false)
const adjustingId = ref(null)

const years = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - 1 + i)

const filters = reactive({ year: null, status: null })

const form = reactive({
  department_id: 1,
  expense_type_id: 1,
  year: new Date().getFullYear(),
  quarter: null,
  amount: 0,
})

const adjustForm = reactive({
  adjustment_amount: 0,
  reason: '',
})

function usagePercent(row) {
  if (row.amount === 0) return 0
  return Math.round((row.used_amount / row.amount) * 100)
}

function progressColor(row) {
  const pct = usagePercent(row)
  if (pct >= 90) return '#F56C6C'
  if (pct >= 80) return '#E6A23C'
  return '#409EFF'
}

function statusTag(status) {
  return { draft: 'info', submitted: 'warning', approved: 'success', rejected: 'danger' }[status] || 'info'
}

function statusLabel(status) {
  return { draft: '草稿', submitted: '已提交', approved: '已审批', rejected: '已驳回' }[status] || status
}

async function fetchBudgets() {
  loading.value = true
  try {
    const params = {}
    if (filters.year) params.year = filters.year
    if (filters.status) params.status = filters.status
    budgets.value = await getBudgets(params)
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  creating.value = true
  try {
    await createBudget({
      department_id: form.department_id,
      expense_type_id: form.expense_type_id,
      year: form.year,
      quarter: form.quarter,
      amount: form.amount,
    })
    ElMessage.success('预算创建成功')
    showCreateDialog.value = false
    fetchBudgets()
  } finally {
    creating.value = false
  }
}

async function handleSubmit(id) {
  try {
    await submitBudget(id)
    ElMessage.success('已提交审批')
    fetchBudgets()
  } catch { /* error handled by interceptor */ }
}

function openAdjust(row) {
  adjustingId.value = row.id
  adjustForm.adjustment_amount = 0
  adjustForm.reason = ''
  showAdjustDialog.value = true
}

async function handleAdjust() {
  adjusting.value = true
  try {
    await adjustBudget(adjustingId.value, {
      adjustment_amount: adjustForm.adjustment_amount,
      reason: adjustForm.reason,
    })
    ElMessage.success('预算调整成功')
    showAdjustDialog.value = false
    fetchBudgets()
  } finally {
    adjusting.value = false
  }
}

onMounted(fetchBudgets)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter-card {
  margin-bottom: 16px;
}
.form-hint {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}
</style>
