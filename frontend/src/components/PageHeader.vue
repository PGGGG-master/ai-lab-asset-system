<template>
  <div class="page-header">
    <div class="page-header-left">
      <div v-if="icon" class="page-header-icon" :style="{ background: iconBg }">
        <el-icon><component :is="icon" /></el-icon>
      </div>
      <div>
        <h2 class="page-header-title">{{ title }}</h2>
        <p v-if="subtitle" class="page-header-sub">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="$slots.default" class="page-header-actions">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' },
  iconBg: {
    type: String,
    default: 'linear-gradient(135deg, #3b82f6, #6366f1)',
  },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.page-header-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.25);
  flex-shrink: 0;
}

.page-header-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.page-header-sub {
  margin: 4px 0 0;
  font-size: 13px;
  color: #94a3b8;
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
