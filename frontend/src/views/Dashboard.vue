<template>
  <div class="dashboard animate-in">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h1>欢迎回来，{{ user?.username }}</h1>
        <p>AI 实验室资产管理系统 · 基于 RBAC 的访问控制</p>
      </div>
      <div class="welcome-roles">
        <el-tag v-for="r in user?.roles" :key="r" effect="dark" round>{{ r }}</el-tag>
      </div>
    </div>

    <el-row :gutter="16" class="stats">
      <el-col :xs="12" :sm="12" :md="6" v-for="(s, i) in statCards" :key="s.label">
        <div class="stat-card" :style="{ animationDelay: `${i * 0.08}s` }">
          <div class="stat-icon" :style="{ background: s.bg }">
            <el-icon><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
          <div class="stat-glow" :style="{ background: s.glow }"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="section-row">
      <el-col :span="24">
        <el-card class="user-card">
          <template #header>
            <div class="card-header-row">
              <el-icon class="card-header-icon"><User /></el-icon>
              <span class="card-title">当前用户</span>
            </div>
          </template>
          <div class="user-info">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ user?.username }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">角色</span>
              <div class="tags-wrap">
                <el-tag v-for="r in user?.roles" :key="r" effect="plain" round>{{ r }}</el-tag>
              </div>
            </div>
            <div class="info-item">
              <span class="info-label">权限数量</span>
              <span class="info-value highlight">{{ user?.permissions?.length || 0 }}</span>
            </div>
          </div>
          <el-collapse class="perm-collapse">
            <el-collapse-item title="查看全部权限">
              <div class="tags-wrap">
                <el-tag v-for="p in user?.permissions" :key="p" size="small" type="info" effect="plain">{{ p }}</el-tag>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="logs-card">
      <template #header>
        <div class="card-header-row">
          <el-icon class="card-header-icon"><Document /></el-icon>
          <span class="card-title">最近操作日志</span>
        </div>
      </template>
      <el-table v-if="stats?.recent_logs?.length" :data="stats.recent_logs" size="small" stripe class="data-table">
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="action" label="操作" width="120">
          <template #default="{ row }">
            <span class="action-pill">{{ row.action }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.result === '成功' ? 'success' : 'danger'" size="small" effect="light">{{ row.result }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
      </el-table>
      <el-empty v-else description="暂无操作记录" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../api'
import { getUser } from '../utils/permission'
import { formatTime } from '../utils/format'

const user = computed(() => getUser())
const stats = ref(null)

const statCards = computed(() => [
  { label: '用户总数', value: stats.value?.user_count ?? '-', icon: 'User', bg: 'linear-gradient(135deg, #3b82f6, #60a5fa)', glow: 'rgba(59,130,246,0.15)' },
  { label: '资产总数', value: stats.value?.asset_count ?? '-', icon: 'FolderOpened', bg: 'linear-gradient(135deg, #8b5cf6, #a78bfa)', glow: 'rgba(139,92,246,0.15)' },
  { label: '角色数量', value: stats.value?.role_count ?? '-', icon: 'Key', bg: 'linear-gradient(135deg, #06b6d4, #22d3ee)', glow: 'rgba(6,182,212,0.15)' },
  { label: '日志条数', value: stats.value?.log_count ?? '-', icon: 'Document', bg: 'linear-gradient(135deg, #f59e0b, #fbbf24)', glow: 'rgba(245,158,11,0.15)' },
])

onMounted(async () => {
  const { data } = await api.get('/auth/dashboard')
  stats.value = data
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding: 24px 28px;
  margin-bottom: 20px;
  border-radius: var(--card-radius);
  background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 50%, #4f46e5 100%);
  color: #fff;
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.25);
  position: relative;
  overflow: hidden;
}

.welcome-banner::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  pointer-events: none;
}

.welcome-text {
  position: relative;
  z-index: 1;
}

.welcome-text h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.welcome-text p {
  margin: 6px 0 0;
  font-size: 13px;
  opacity: 0.85;
}

.welcome-roles {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.welcome-roles .el-tag {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  animation: fadeInUp 0.5s ease both;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.stat-glow {
  position: absolute;
  right: -20px;
  top: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  filter: blur(24px);
  opacity: 0.6;
  pointer-events: none;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}

.stat-label {
  color: #64748b;
  font-size: 13px;
  margin-top: 2px;
}

.section-row { margin-top: 20px; }

.card-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header-icon {
  color: #3b82f6;
  font-size: 18px;
}

.card-title {
  font-weight: 600;
  color: #334155;
}

.user-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 12px;
  color: #94a3b8;
}

.info-value {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
}

.info-value.highlight {
  color: #3b82f6;
  font-size: 20px;
  font-weight: 700;
}

.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.perm-collapse {
  margin-top: 8px;
  border: none;
}

.perm-collapse :deep(.el-collapse-item__header) {
  border: none;
  color: #64748b;
  font-size: 13px;
}

.logs-card { margin-top: 20px; }

.action-pill {
  display: inline-block;
  padding: 2px 8px;
  background: #f1f5f9;
  border-radius: 4px;
  font-size: 12px;
  color: #475569;
}

@media (max-width: 900px) {
  .user-info { grid-template-columns: 1fr; }
  .stats :deep(.el-col) { margin-bottom: 12px; }
}
</style>
