<template>
  <el-container class="layout">
    <el-aside width="228px" class="aside">
      <div class="logo">
        <div class="logo-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="logo-text">
          <span class="logo-title">AI 实验室</span>
          <span class="logo-sub">资产管理系统</span>
        </div>
      </div>
      <el-menu
        :default-active="route.path"
        router
        class="side-menu"
        background-color="transparent"
        text-color="rgba(255,255,255,0.75)"
        active-text-color="#fff"
      >
        <el-menu-item v-for="m in visibleMenus" :key="m.path" :index="m.path" class="menu-item">
          <el-icon><component :is="m.icon" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="right-panel">
      <el-header class="header">
        <div class="header-left">
          <span class="title">{{ currentTitle }}</span>
          <span class="subtitle">RBAC 访问控制</span>
        </div>
        <div class="user-area">
          <el-tag v-for="r in user?.roles" :key="r" size="small" effect="plain" class="role-tag">{{ r }}</el-tag>
          <div class="user-badge">
            <el-icon><User /></el-icon>
            <span>{{ user?.username }}</span>
          </div>
          <el-button class="logout-btn" round size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearAuth, getUser, hasPermission } from '../utils/permission'

const route = useRoute()
const router = useRouter()
const user = computed(() => getUser())

const menus = [
  { path: '/dashboard', title: '首页', icon: 'HomeFilled', permission: null },
  { path: '/assets', title: '资产管理', icon: 'FolderOpened', permission: 'asset:read' },
  { path: '/users', title: '用户管理', icon: 'User', permission: 'user:manage' },
  { path: '/roles', title: '角色权限', icon: 'Key', permission: 'role:manage' },
  { path: '/logs', title: '操作日志', icon: 'Document', permission: 'log:view' },
]

const visibleMenus = computed(() =>
  menus.filter((m) => !m.permission || hasPermission(m.permission))
)

const currentTitle = computed(() => menus.find((m) => m.path === route.path)?.title || '系统')

function logout() {
  clearAuth()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: var(--app-bg);
}

.aside {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.logo-title {
  color: #fff;
  font-weight: 600;
  font-size: 15px;
}

.logo-sub {
  color: rgba(255, 255, 255, 0.45);
  font-size: 11px;
}

.side-menu {
  border-right: none;
  padding: 12px 10px;
  flex: 1;
}

.side-menu :deep(.el-menu-item) {
  border-radius: 8px;
  margin-bottom: 4px;
  height: 44px;
  transition: all 0.2s ease;
}

.side-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
  transform: translateX(2px);
}

.side-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.35), rgba(99, 102, 241, 0.2)) !important;
  color: #fff !important;
  font-weight: 500;
  box-shadow: inset 3px 0 0 #60a5fa;
}

.right-panel {
  min-width: 0;
  overflow: visible;
}

.header {
  height: 60px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.role-tag {
  border-color: #e2e8f0;
  color: #64748b;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: #f1f5f9;
  border-radius: 20px;
  font-size: 13px;
  color: #475569;
}

.logout-btn {
  border: 1px solid #fecaca;
  color: #ef4444;
  background: #fff;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #fef2f2;
  border-color: #ef4444;
  color: #dc2626;
}

.main {
  padding: 24px;
  overflow: visible;
}
</style>
