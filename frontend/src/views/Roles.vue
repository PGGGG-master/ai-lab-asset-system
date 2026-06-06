<template>
  <div class="page animate-in">
    <PageHeader
      title="角色权限"
      subtitle="配置 RBAC 角色与权限映射"
      icon="Key"
      icon-bg="linear-gradient(135deg, #06b6d4, #22d3ee)"
    />

    <el-row :gutter="16">
      <el-col :span="14">
        <el-card>
          <template #header>
            <span class="card-label">角色列表</span>
          </template>
          <el-table
            v-if="roles.length || loading"
            :data="roles"
            v-loading="loading"
            highlight-current-row
            @row-click="selectRole"
          >
            <el-table-column prop="role_name" label="角色名" width="140">
              <template #default="{ row }">
                <span class="role-name">{{ row.role_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
            <el-table-column label="权限数" width="90" align="center">
              <template #default="{ row }">
                <el-badge :value="row.permissions?.length || 0" type="primary" />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无角色" :image-size="80" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card class="perm-card" :class="{ active: selected }">
          <template #header>
            <span class="card-label">
              {{ selected ? `权限配置：${selected.role_name}` : '请选择角色' }}
            </span>
          </template>
          <template v-if="selected">
            <div class="perm-scroll">
              <el-checkbox-group v-model="selectedPermIds">
                <label v-for="p in permissions" :key="p.id" class="perm-item">
                  <el-checkbox :label="p.id">
                    <span class="perm-name">{{ p.permission_name }}</span>
                    <code class="perm-code">{{ p.permission_code }}</code>
                  </el-checkbox>
                </label>
              </el-checkbox-group>
            </div>
            <el-button v-if="canAssign" type="primary" round style="margin-top:16px;width:100%" @click="savePerms">
              保存权限
            </el-button>
          </template>
          <el-empty v-else description="点击左侧角色进行配置" :image-size="80" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'
import api from '../api'
import { hasPermission } from '../utils/permission'

const roles = ref([])
const permissions = ref([])
const loading = ref(false)
const selected = ref(null)
const selectedPermIds = ref([])
const canAssign = computed(() => hasPermission('permission:manage'))

async function load() {
  loading.value = true
  try {
    const [r, p] = await Promise.all([api.get('/roles'), api.get('/permissions')])
    roles.value = r.data
    permissions.value = p.data
  } finally {
    loading.value = false
  }
}

function selectRole(row) {
  selected.value = row
  selectedPermIds.value = permissions.value
    .filter((p) => row.permissions.includes(p.permission_code))
    .map((p) => p.id)
}

async function savePerms() {
  await api.put(`/roles/${selected.value.id}/permissions`, { permission_ids: selectedPermIds.value })
  ElMessage.success('权限已保存')
  load()
}

onMounted(load)
</script>

<style scoped>
.card-label {
  font-weight: 600;
  color: #334155;
}

.role-name {
  font-weight: 500;
  color: #0f172a;
}

.perm-card {
  transition: border-color 0.2s ease;
}

.perm-card.active {
  border-color: rgba(59, 130, 246, 0.4);
}

.perm-item {
  display: block;
  padding: 10px 12px;
  margin-bottom: 6px;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
  transition: background 0.15s ease, border-color 0.15s ease;
  cursor: pointer;
}

.perm-item:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.perm-name {
  display: block;
  font-size: 14px;
  color: #1e293b;
}

.perm-code {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
  background: none;
}
</style>
