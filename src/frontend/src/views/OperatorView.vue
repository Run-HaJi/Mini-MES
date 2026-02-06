<template>
  <div class="page-container">
    <div class="header">
      <h2 class="title">👷‍♂️ 人员信息管理</h2>
      <el-button type="primary" icon="Plus" @click="openDialog()">新增工人</el-button>
    </div>

    <el-table :data="tableData" border stripe style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="姓名" width="120">
        <template #default="scope">
          <el-tag effect="plain">{{ scope.row.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="code" label="工号 (唯一)" width="150" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
            {{ scope.row.is_active ? '在职' : '离职' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" @click="openDialog(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工人' : '新增工人'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="工号">
          <el-input v-model="form.code" placeholder="建议使用拼音或编号" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-switch v-model="form.is_active" active-text="在职" inactive-text="离职" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const tableData = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({ id: null, name: '', code: '', is_active: true })

// 1. 获取列表
const fetchList = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/v1/operators/')
    const data = await res.json()
    tableData.value = data
  } catch (err) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 2. 打开弹窗
const openDialog = (row = null) => {
  if (row) {
    isEdit.value = true
    form.value = { ...row } // 复制数据
  } else {
    isEdit.value = false
    form.value = { name: '', code: '', role: 'worker', is_active: true }
  }
  dialogVisible.value = true
}

// 3. 提交 (新增或修改)
const handleSubmit = async () => {
  const url = isEdit.value ? `/api/v1/operators/${form.value.id}` : '/api/v1/operators/'
  const method = isEdit.value ? 'PUT' : 'POST'
  
  try {
    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    if (res.ok) {
      ElMessage.success('操作成功')
      dialogVisible.value = false
      fetchList() // 刷新列表
    } else {
      const err = await res.json()
      ElMessage.error(err.detail || '操作失败')
    }
  } catch (error) {
    ElMessage.error('网络错误')
  }
}

// 4. 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除工人 ${row.name} 吗?`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await fetch(`/api/v1/operators/${row.id}`, { method: 'DELETE' })
    ElMessage.success('已删除')
    fetchList()
  })
}

onMounted(() => fetchList())
</script>

<style scoped>
.page-container { padding: 20px; color: #fff; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.title { margin: 0; font-size: 20px; }
</style>