<template>
  <div class="login-page">
    <!-- 动态背景层（全程可见） -->
    <div class="login-bg" aria-hidden="true">
      <div class="bg-mesh"></div>
      <div class="bg-aurora"></div>
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
      <div class="particles">
        <span
          v-for="p in particles"
          :key="p.id"
          class="particle"
          :style="{
            left: p.x + '%',
            top: p.y + '%',
            width: p.size + 'px',
            height: p.size + 'px',
            animationDelay: p.delay + 's',
            animationDuration: p.duration + 's',
            opacity: p.opacity,
          }"
        />
      </div>
      <svg class="bg-lines" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="lineGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="rgba(59,130,246,0)" />
            <stop offset="50%" stop-color="rgba(59,130,246,0.35)" />
            <stop offset="100%" stop-color="rgba(59,130,246,0)" />
          </linearGradient>
        </defs>
        <path class="line-path line-1" d="M0,450 Q360,200 720,450 T1440,450" />
        <path class="line-path line-2" d="M0,600 Q480,350 960,600 T1440,600" />
        <path class="line-path line-3" d="M0,300 Q400,550 800,300 T1440,300" />
      </svg>
      <div class="grid-overlay"></div>
      <div class="bg-vignette"></div>
    </div>

    <!-- 入场演示动画 -->
    <Transition name="splash-out">
      <div v-if="showIntro" class="intro-splash" @click="skipIntro">
        <div class="intro-inner">
          <div class="intro-logo-wrap">
            <div class="intro-ring intro-ring-1"></div>
            <div class="intro-ring intro-ring-2"></div>
            <div class="intro-logo">
              <el-icon><Monitor /></el-icon>
            </div>
          </div>

          <h1 class="intro-title">AI 实验室资产管理系统</h1>
          <p class="intro-sub">基于 RBAC 的软件安全实验平台</p>

          <div class="intro-flow">
            <div
              v-for="(step, i) in introSteps"
              :key="step.label"
              class="flow-step"
              :class="{ active: introStep >= i, current: introStep === i }"
            >
              <div class="flow-icon">
                <el-icon><component :is="step.icon" /></el-icon>
              </div>
              <span class="flow-label">{{ step.label }}</span>
              <div v-if="i < introSteps.length - 1" class="flow-line" :class="{ active: introStep > i }"></div>
            </div>
          </div>

          <p class="intro-desc">{{ introSteps[introStep]?.desc }}</p>

          <div class="intro-progress">
            <div class="intro-progress-bar" :style="{ width: progress + '%' }"></div>
          </div>
          <p class="intro-skip">点击任意处跳过 · {{ skipCountdown }}s 后进入登录</p>
        </div>
      </div>
    </Transition>

    <!-- 登录表单 -->
    <Transition name="card-in">
      <el-card v-if="!showIntro" class="login-card" shadow="never">
        <div class="login-brand">
          <div class="brand-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <h2>AI 实验室资产管理系统</h2>
          <p>基于 RBAC 的访问控制 · 软件安全实验</p>
        </div>

        <el-form :model="form" class="login-form" @submit.prevent="onLogin">
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="admin" size="large" :prefix-icon="User" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="admin123"
              size="large"
              :prefix-icon="Lock"
              @keyup.enter="onLogin"
            />
          </el-form-item>
          <el-button type="primary" :loading="loading" size="large" class="login-btn" @click="onLogin">
            登 录
          </el-button>
        </el-form>

        <el-collapse class="demo-collapse">
          <el-collapse-item title="演示账号（点击展开，点击行填入）" name="demo">
            <el-table :data="demoAccounts" size="small" class="demo-table" @row-click="fillAccount">
              <el-table-column prop="username" label="账号" width="90" />
              <el-table-column prop="role" label="角色" />
              <el-table-column prop="password" label="密码" width="100" />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </Transition>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { setAuth } from '../utils/permission'

const router = useRouter()
const loading = ref(false)
const showIntro = ref(true)
const introStep = ref(0)
const progress = ref(0)
const skipCountdown = ref(1)
const form = ref({ username: 'admin', password: 'admin123' })

const particles = Array.from({ length: 36 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: 1.5 + Math.random() * 2.5,
  delay: Math.random() * 6,
  duration: 5 + Math.random() * 8,
  opacity: 0.15 + Math.random() * 0.45,
}))

const introSteps = [
  { icon: 'User', label: '用户认证', desc: 'JWT 令牌 · bcrypt 密码加密 · 安全登录' },
  { icon: 'Key', label: '角色授权', desc: '7 种角色 · 细粒度权限 · 前后端双重校验' },
  { icon: 'FolderOpened', label: '资产管理', desc: '模型 / 数据集 / 报告 · 多格式文件管理' },
  { icon: 'Document', label: '审计追踪', desc: '登录与越权操作 · 全程日志记录' },
]

const demoAccounts = [
  { username: 'admin', role: '系统管理员', password: 'admin123' },
  { username: 'leader', role: '项目负责人', password: 'leader123' },
  { username: 'modeler', role: '模型管理员', password: 'modeler123' },
  { username: 'dataer', role: '数据管理员', password: 'dataer123' },
  { username: 'member', role: '实验成员', password: 'member123' },
  { username: 'auditor', role: '安全审计员', password: 'auditor123' },
  { username: 'guest', role: '访客', password: 'guest123' },
]

let stepTimer = null
let countdownTimer = null
let progressTimer = null
let finishTimer = null

function skipIntro() {
  showIntro.value = false
  clearTimers()
}

function clearTimers() {
  clearInterval(stepTimer)
  clearInterval(countdownTimer)
  clearInterval(progressTimer)
  clearTimeout(finishTimer)
}

onMounted(() => {
  const totalMs = 1000
  const stepMs = totalMs / introSteps.length

  stepTimer = setInterval(() => {
    if (introStep.value < introSteps.length - 1) {
      introStep.value += 1
    }
  }, stepMs)

  progressTimer = setInterval(() => {
    progress.value = Math.min(100, progress.value + 1.2)
  }, totalMs / 85)

  countdownTimer = setInterval(() => {
    skipCountdown.value -= 1
    if (skipCountdown.value <= 0) {
      skipIntro()
    }
  }, 1000)

  finishTimer = setTimeout(skipIntro, totalMs)
})

onUnmounted(clearTimers)

function fillAccount(row) {
  form.value.username = row.username
  form.value.password = row.password
}

async function onLogin() {
  loading.value = true
  try {
    const { data } = await api.post('/auth/login', form.value)
    setAuth(data.access_token, data.user)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 24px;
  background: #070b14;
}

/* ===== 动态背景 ===== */
.login-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-mesh {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 90% 70% at 15% 25%, rgba(37, 99, 235, 0.45), transparent 55%),
    radial-gradient(ellipse 70% 60% at 85% 75%, rgba(99, 102, 241, 0.38), transparent 50%),
    radial-gradient(ellipse 55% 45% at 55% 15%, rgba(6, 182, 212, 0.22), transparent 45%),
    radial-gradient(ellipse 40% 35% at 70% 40%, rgba(139, 92, 246, 0.18), transparent 40%),
    linear-gradient(160deg, #070b14 0%, #0f172a 40%, #0c1929 70%, #0a1628 100%);
  animation: meshShift 18s ease-in-out infinite alternate;
}

@keyframes meshShift {
  0% { filter: hue-rotate(0deg) brightness(1); transform: scale(1); }
  100% { filter: hue-rotate(12deg) brightness(1.05); transform: scale(1.03); }
}

.bg-aurora {
  position: absolute;
  inset: -40%;
  background: conic-gradient(
    from 200deg at 50% 50%,
    transparent 0deg,
    rgba(59, 130, 246, 0.07) 60deg,
    transparent 120deg,
    rgba(139, 92, 246, 0.06) 200deg,
    transparent 280deg,
    rgba(6, 182, 212, 0.05) 340deg,
    transparent 360deg
  );
  animation: auroraSpin 30s linear infinite;
}

@keyframes auroraSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.bg-shapes {
  position: absolute;
  inset: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  animation: float 14s ease-in-out infinite;
}

.shape-1 {
  width: 420px; height: 420px;
  background: #2563eb;
  top: -120px; left: -100px;
  opacity: 0.55;
}
.shape-2 {
  width: 360px; height: 360px;
  background: #6366f1;
  bottom: -100px; right: -80px;
  animation-delay: -5s;
  opacity: 0.45;
}
.shape-3 {
  width: 260px; height: 260px;
  background: #06b6d4;
  top: 35%; right: 12%;
  animation-delay: -9s;
  opacity: 0.3;
}
.shape-4 {
  width: 200px; height: 200px;
  background: #8b5cf6;
  bottom: 20%; left: 8%;
  animation-delay: -3s;
  opacity: 0.25;
}

.particles {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 6px rgba(147, 197, 253, 0.8);
  animation: particleFloat linear infinite;
}

@keyframes particleFloat {
  0%, 100% { transform: translateY(0) translateX(0); opacity: 0.2; }
  25% { transform: translateY(-18px) translateX(6px); }
  50% { transform: translateY(-8px) translateX(-4px); opacity: 0.7; }
  75% { transform: translateY(-22px) translateX(3px); }
}

.bg-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.35;
}

.line-path {
  fill: none;
  stroke-width: 1;
  stroke-linecap: round;
}

.line-1 {
  stroke: url(#lineGrad1);
  stroke-dasharray: 8 12;
  animation: lineFlow 20s linear infinite;
}

.line-2 {
  stroke: rgba(99, 102, 241, 0.25);
  stroke-dasharray: 4 16;
  animation: lineFlow 28s linear infinite reverse;
}

.line-3 {
  stroke: rgba(6, 182, 212, 0.2);
  stroke-dasharray: 6 10;
  animation: lineFlow 24s linear infinite;
  animation-delay: -8s;
}

@keyframes lineFlow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -400; }
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse 80% 70% at 50% 45%, black 15%, transparent 75%);
  animation: gridPulse 8s ease-in-out infinite alternate;
}

@keyframes gridPulse {
  from { opacity: 0.6; }
  to { opacity: 1; }
}

.bg-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, transparent 40%, rgba(7, 11, 20, 0.65) 100%);
}

/* SVG 线条已在 template 内定义渐变 */

/* ===== 入场演示 ===== */
.intro-splash {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(7, 11, 20, 0.35);
  backdrop-filter: blur(3px);
  cursor: pointer;
}

.intro-inner {
  text-align: center;
  color: #fff;
  padding: 24px;
  max-width: 640px;
  animation: introFadeIn 0.6s ease both;
  position: relative;
  z-index: 1;
}

@keyframes introFadeIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.intro-logo-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 28px;
}

.intro-logo {
  position: absolute;
  inset: 0;
  margin: auto;
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  box-shadow: 0 0 40px rgba(59, 130, 246, 0.5);
  animation: logoPulse 2s ease-in-out infinite;
  z-index: 2;
}

.intro-ring {
  position: absolute;
  inset: 0;
  margin: auto;
  border-radius: 50%;
  border: 2px solid rgba(59, 130, 246, 0.4);
  animation: ringExpand 2s ease-out infinite;
}

.intro-ring-2 {
  animation-delay: 1s;
}

@keyframes logoPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 40px rgba(59, 130, 246, 0.5); }
  50% { transform: scale(1.05); box-shadow: 0 0 60px rgba(99, 102, 241, 0.6); }
}

@keyframes ringExpand {
  0% { width: 72px; height: 72px; opacity: 0.8; }
  100% { width: 120px; height: 120px; opacity: 0; }
}

.intro-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(90deg, #fff, #93c5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.intro-sub {
  margin: 10px 0 36px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.55);
}

.intro-flow {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.flow-step {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
  opacity: 0.35;
  transform: translateY(8px);
  transition: all 0.45s cubic-bezier(0.4, 0, 0.2, 1);
}

.flow-step.active {
  opacity: 1;
  transform: translateY(0);
}

.flow-step.current .flow-icon {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  box-shadow: 0 0 24px rgba(59, 130, 246, 0.6);
  transform: scale(1.1);
}

.flow-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  transition: all 0.4s ease;
  margin-bottom: 8px;
}

.flow-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
}

.flow-line {
  position: absolute;
  top: 24px;
  left: calc(50% + 28px);
  width: calc(100% - 56px);
  height: 2px;
  background: rgba(255, 255, 255, 0.12);
  transition: background 0.4s ease;
}

.flow-line.active {
  background: linear-gradient(90deg, #3b82f6, #6366f1);
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

.intro-desc {
  min-height: 22px;
  font-size: 14px;
  color: rgba(147, 197, 253, 0.9);
  margin: 0 0 28px;
  transition: opacity 0.3s ease;
}

.intro-progress {
  width: 280px;
  height: 3px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 2px;
  margin: 0 auto 16px;
  overflow: hidden;
}

.intro-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  border-radius: 2px;
  transition: width 0.05s linear;
}

.intro-skip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0;
}

/* 过渡 */
.splash-out-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.splash-out-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

.card-in-enter-active {
  transition: opacity 0.55s ease 0.1s, transform 0.55s cubic-bezier(0.34, 1.2, 0.64, 1) 0.1s;
}
.card-in-enter-from {
  opacity: 0;
  transform: translateY(24px) scale(0.96);
}

/* ===== 登录卡片 ===== */
.login-card {
  width: 100%;
  max-width: 460px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px) saturate(1.4);
  -webkit-backdrop-filter: blur(24px) saturate(1.4);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08) inset,
    0 24px 48px rgba(0, 0, 0, 0.35),
    0 0 80px rgba(59, 130, 246, 0.12);
  position: relative;
  z-index: 10;
  padding: 8px 4px 4px;
}

.login-brand { text-align: center; margin-bottom: 8px; }

.brand-icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 12px;
  border-radius: 14px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 26px;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
}

.login-brand h2 { margin: 0; font-size: 20px; color: #0f172a; font-weight: 600; }
.login-brand p { margin: 8px 0 0; color: #64748b; font-size: 13px; }
.login-form { margin-top: 20px; }

.login-btn {
  width: 100%;
  margin-top: 4px;
  font-weight: 500;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

.demo-collapse { margin-top: 16px; border: none; }
.demo-collapse :deep(.el-collapse-item__header) { font-size: 13px; color: #64748b; border: none; height: 40px; }
.demo-collapse :deep(.el-collapse-item__wrap) { border: none; }
.demo-table { border-radius: 8px; overflow: hidden; cursor: pointer; }
.demo-table :deep(.el-table__row:hover) { background: #eff6ff !important; }

@media (prefers-reduced-motion: reduce) {
  .bg-mesh, .bg-aurora, .shape, .particle, .line-path, .grid-overlay {
    animation: none !important;
  }
}

@media (max-width: 520px) {
  .intro-flow { gap: 8px; }
  .flow-step { width: 72px; }
  .flow-line { display: none; }
  .intro-title { font-size: 22px; }
}
</style>
