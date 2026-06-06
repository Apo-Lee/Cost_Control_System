<template>
  <div class="expense-page">
    <div class="page-header">
      <h2>费用报销</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增报销单
      </el-button>
    </div>

    <!-- 筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部" style="width: 130px">
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已审批" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchExpenses">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card>
      <el-table :data="expenses" v-loading="loading" stripe>
        <el-table-column prop="report_no" label="报销单号" width="180" />
        <el-table-column prop="title" label="事由" min-width="180" />
        <el-table-column label="金额" width="120">
          <template #default="{ row }">¥{{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'draft'"
              type="success"
              size="small"
              @click="handleSubmit(row.id)"
            >
              提交
            </el-button>
            <el-button size="small" @click="openUpload(row)">
              <el-icon><Upload /></el-icon>
              上传
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增报销单弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新增报销单" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="部门ID">
          <el-input-number v-model="form.department_id" :min="1" />
        </el-form-item>
        <el-form-item label="费用类型ID">
          <el-input-number v-model="form.expense_type_id" :min="1" />
        </el-form-item>
        <el-form-item label="报销事由">
          <el-input v-model="form.title" placeholder="简要说明报销内容" />
        </el-form-item>
        <el-form-item label="报销金额">
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" :step="100" />
        </el-form-item>
        <el-form-item label="详细说明">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传附件弹窗 -->
    <el-dialog v-model="showUploadDialog" title="上传发票" width="450px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="onFileChange"
        :limit="1"
        accept="image/*,.pdf"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或点击上传</div>
        <template #tip>
          <div class="el-upload__tip">支持 jpg/png/pdf 文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Upload, UploadFilled } from '@element-plus/icons-vue'
import { getExpenses, createExpense, submitExpense, uploadAttachment } from '../../api/expense'

const loading = ref(false)
const creating = ref(false)
const uploading = ref(false)
const expenses = ref([])
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const uploadingId = ref(null)
const selectedFile = ref(null)

const filters = reactive({ status: null })

const form = reactive({
  department_id: 1,
  expense_type_id: 1,
  title: '',
  amount: 0,
  description: '',
})

function statusTag(s) {
  return { draft: 'info', submitted: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info'
}

function statusLabel(s) {
  return { draft: '草稿', submitted: '已提交', approved: '已审批', rejected: '已驳回' }[s] || s
}

function onFileChange(file) {
  selectedFile.value = file.raw
}

async function fetchExpenses() {
  loading.value = true
  try {
    const params = {}
    if (filters.status) params.status = filters.status
    expenses.value = await getExpenses(params)
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  creating.value = true
  try {
    await createExpense({
      department_id: form.department_id,
      expense_type_id: form.expense_type_id,
      title: form.title,
      amount: form.amount,
      description: form.description || null,
    })
    ElMessage.success('报销单创建成功')
    showCreateDialog.value = false
    form.title = ''
    fetchExpenses()
  } finally {
    creating.value = false
  }
}

async function handleSubmit(id) {
  try {
    await submitExpense(id)
    ElMessage.success('已提交审批')
    fetchExpenses()
  } catch {}
}

function openUpload(row) {
  uploadingId.value = row.id
  selectedFile.value = null
  showUploadDialog.value = true
}

async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    await uploadAttachment(uploadingId.value, selectedFile.value)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
  } finally {
    uploading.value = false
  }
}

onMounted(fetchExpenses)
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
</style>
