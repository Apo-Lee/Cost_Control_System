<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">¥{{ data.month_total.toFixed(2) }}</div>
            <div class="stat-label">本月报销总额</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value" style="color: #E6A23C">{{ data.pending_count }}</div>
            <div class="stat-label">待审批</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ data.budget_count }}</div>
            <div class="stat-label">预算总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ roleLabel }}</div>
            <div class="stat-label">当前角色</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <p style="color: #909399; text-align: center;">
        👋 欢迎使用费控系统！请通过左侧菜单导航到各功能模块。
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/index'

const authStore = useAuthStore()

const data = ref({ month_total: 0, pending_count: 0, budget_count: 0 })

const roleLabels = { admin: '管理员', manager: '部门经理', finance: '财务', employee: '员工' }
const roleLabel = computed(() => roleLabels[authStore.userRole] || authStore.userRole)

onMounted(async () => {
  try {
    data.value = await api.get('/reports/dashboard')
  } catch {}
})
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
