<template>
  <div class="page animate-in">
    <PageHeader
      title="操作日志"
      subtitle="登录、文件操作及越权访问记录"
      icon="Document"
      icon-bg="linear-gradient(135deg, #f59e0b, #fbbf24)"
    />

    <el-card>
      <el-table v-if="logs.length || loading" :data="logs" v-loading="loading" stripe size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="action" label="操作" width="130">
          <template #default="{ row }">
            <span class="action-tag" :class="actionClass(row.action)">{{ row.action }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="对象类型" width="100" />
        <el-table-column prop="target_id" label="对象ID" width="100" show-overflow-tooltip />
        <el-table-column prop="result" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.result === '成功' ? 'success' : 'danger'" size="small" effect="light" round>
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP" width="120" />
      </el-table>
      <el-empty v-else description="暂无日志记录" :image-size="100" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import api from '../api'
import { formatTime } from '../utils/format'

const logs = ref([])
const loading = ref(false)

function actionClass(action) {
  if (action === 'LOGIN') return 'act-login'
  if (action === 'DENY') return 'act-deny'
  if (['UPLOAD', 'DOWNLOAD', 'DELETE'].includes(action)) return 'act-file'
  return 'act-default'
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await api.get('/logs')
    logs.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.action-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.act-login { background: #eff6ff; color: #2563eb; }
.act-deny { background: #fef2f2; color: #dc2626; }
.act-file { background: #f0fdf4; color: #16a34a; }
.act-default { background: #f1f5f9; color: #475569; }
</style>
