<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in cards" :key="card.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.title }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <p style="color: #909399; margin-top: 40px; text-align: center;">
      更多统计功能将在后续步骤中实现
    </p>
  </div>
</template>

<script setup>
const cards = [
  { title: '本月报销', value: '¥0.00' },
  { title: '待审批', value: '0' },
  { title: '预算执行率', value: '0%' },
  { title: '部门费用排名', value: '-' },
]
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
