import { createRouter, createWebHistory } from 'vue-router'
import { getUser } from '../utils/permission'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'assets', name: 'Assets', component: () => import('../views/Assets.vue') },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue'), meta: { perm: 'user:manage' } },
      { path: 'roles', name: 'Roles', component: () => import('../views/Roles.vue'), meta: { perm: 'role:manage' } },
      { path: 'logs', name: 'Logs', component: () => import('../views/Logs.vue'), meta: { perm: 'log:view' } },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta.public) return true
  const user = getUser()
  if (!user) return '/login'
  if (to.meta.perm) {
    const perms = user.permissions || []
    if (!perms.includes(to.meta.perm)) return '/dashboard'
  }
  return true
})

export default router
