<template>
  <div class="page animate-in">
    <PageHeader
      title="用户管理"
      subtitle="创建用户、分配角色与账号状态"
      icon="User"
      icon-bg="linear-gradient(135deg, #3b82f6, #60a5fa)"
    >
      <el-button type="primary" round @click="openCreate">
        <el-icon><Plus /></el-icon> 新增用户
      </el-button>
    </PageHeader>

    <el-card>
      <el-table v-if="users.length || loading" :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="avatar">{{ row.username.charAt(0).toUpperCase() }}</span>
              <span>{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" effect="light" round>
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="roles" label="角色">
          <template #default="{ row }">
            <el-tag v-for="r in row.roles" :key="r" size="small" effect="plain" round style="margin:2px">{{ r }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button link type="primary" @click="openRoles(row)">分配角色</el-button>
            <el-button link type="warning" @click="resetPwd(row)">重置密码</el-button>
            <el-button link :type="row.status === 'active' ? 'danger' : 'success'" @click="toggleStatus(row)">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无用户" :image-size="100" />
    </el-card>

    <el-dialog v-model="showCreate" title="新增用户" width="440px" destroy-on-close align-center>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple style="width:100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="createUser">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRoles" title="分配角色" width="440px" destroy-on-close align-center>
      <el-select v-model="roleIds" multiple style="width:100%">
        <el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" />
      </el-select>
      <template #footer>
        <el-button @click="showRoles = false">取消</el-button>
        <el-button type="primary" @click="saveRoles">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'
import api from '../api'

const users = ref([])
const roles = ref([])
const loading = ref(false)
const showCreate = ref(false)
const showRoles = ref(false)
const editingUserId = ref(null)
const roleIds = ref([])
const form = ref({ username: '', password: '', role_ids: [] })

async function load() {
  loading.value = true
  try {
    const [u, r] = await Promise.all([api.get('/users'), api.get('/roles')])
    users.value = u.data
    roles.value = r.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.value = { username: '', password: '', role_ids: [] }
  showCreate.value = true
}

async function createUser() {
  await api.post('/users', form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  load()
}

function openRoles(row) {
  editingUserId.value = row.id
  roleIds.value = roles.value.filter((r) => row.roles.includes(r.role_name)).map((r) => r.id)
  showRoles.value = true
}

async function saveRoles() {
  await api.put(`/users/${editingUserId.value}/roles`, { role_ids: roleIds.value })
  ElMessage.success('角色已更新')
  showRoles.value = false
  load()
}

async function resetPwd(row) {
  const { value } = await ElMessageBox.prompt('输入新密码', '重置密码', { inputType: 'password' })
  if (value) {
    await api.put(`/users/${row.id}`, { password: value })
    ElMessage.success('密码已重置')
  }
}

async function toggleStatus(row) {
  const status = row.status === 'active' ? 'disabled' : 'active'
  await api.put(`/users/${row.id}`, { status })
  ElMessage.success('状态已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
