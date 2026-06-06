<template>
  <div class="report-page">
    <h2>报表查询</h2>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">¥{{ dashboard.month_total.toFixed(2) }}</div>
            <div class="stat-label">本月报销总额</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value" style="color: #E6A23C">{{ dashboard.pending_count }}</div>
            <div class="stat-label">待审批报销单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ dashboard.budget_count }}</div>
            <div class="stat-label">预算总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
        <span>预算执行情况</span>
        <el-button type="primary" size="small" @click="exportCSV">
          <el-icon><Download /></el-icon>
          导出 CSV
        </el-button>
      </div>
      <el-table :data="budgets" stripe>
        <el-table-column prop="department_id" label="部门ID" width="100" />
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column label="预算金额" width="140">
          <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="已使用" width="140">
          <template #default="{ row }">¥{{ row.used_amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="执行率" min-width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.execution_rate"
              :color="row.execution_rate >= 80 ? '#E6A23C' : '#409EFF'"
              :stroke-width="18"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import api from '../../api/index'

const dashboard = ref({ month_total: 0, pending_count: 0, budget_count: 0 })
const budgets = ref([])

async function fetchData() {
  try {
    dashboard.value = await api.get('/reports/dashboard')
    budgets.value = await api.get('/reports/budget-execution')
  } catch {}
}

async function exportCSV() {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/reports/export`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'expenses.csv'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
