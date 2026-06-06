<template>
  <div class="page animate-in">
    <PageHeader
      title="资产管理"
      subtitle="上传、预览与下载实验室资产文件"
      icon="FolderOpened"
      icon-bg="linear-gradient(135deg, #8b5cf6, #a78bfa)"
    >
      <el-button v-if="canUpload" type="primary" round @click="showUpload = true">
        <el-icon><Upload /></el-icon>
        上传资产
      </el-button>
    </PageHeader>

    <el-card>
      <div class="filter-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索资产名称..."
          clearable
          style="width: 220px"
          :prefix-icon="Search"
        />
        <el-select v-model="typeFilter" placeholder="全部类型" clearable style="width: 140px">
          <el-option v-for="t in assetTypes" :key="t" :label="t" :value="t" />
        </el-select>
        <span class="filter-count">共 {{ filteredAssets.length }} 项</span>
      </div>

      <el-table
        v-if="filteredAssets.length || loading"
        :data="filteredAssets"
        v-loading="loading"
        stripe
        class="data-table"
      >
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <div class="name-cell">
              <span class="file-badge" :class="extClass(row.file_ext)">{{ row.file_ext || '?' }}</span>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="asset_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="typeColor(row.asset_type)" effect="light" round>{{ row.asset_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="上传者" width="100" />
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.previewable" link type="primary" @click="preview(row)">
              <el-icon><View /></el-icon> 预览
            </el-button>
            <el-button v-if="canDownload" link type="success" @click="download(row)">
              <el-icon><Download /></el-icon> 下载
            </el-button>
            <el-button v-if="canUpdate" link type="warning" @click="edit(row)">
              <el-icon><Edit /></el-icon> 修改
            </el-button>
            <el-button v-if="canDelete" link type="danger" @click="remove(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无匹配的资产" :image-size="100">
        <el-button v-if="canUpload" type="primary" @click="showUpload = true">上传第一个资产</el-button>
      </el-empty>
    </el-card>

    <el-dialog v-model="showUpload" title="上传资产" width="520px" append-to-body destroy-on-close align-center>
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="uploadForm.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="uploadForm.asset_type" style="width:100%" @change="uploadFile = null">
            <el-option v-for="t in assetTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="uploadForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="文件">
          <el-upload
            :key="uploadForm.asset_type"
            drag
            :auto-upload="false"
            :limit="1"
            :accept="acceptForType(uploadForm.asset_type)"
            :on-change="onFileChange"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-tip">拖拽或点击选择</div>
            <template #tip>
              <div class="el-upload__tip">支持：{{ extHint(uploadForm.asset_type) }}</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="doUpload">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showPreview"
      :title="previewData?.name"
      width="680px"
      append-to-body
      destroy-on-close
      align-center
      class="preview-dialog"
    >
      <div v-if="previewData?.file_ext" class="preview-meta">
        <el-tag size="small" effect="plain">{{ previewData.file_ext }}</el-tag>
      </div>
      <pre class="preview-code">{{ previewData?.content }}</pre>
    </el-dialog>

    <el-dialog v-model="showEdit" title="修改资产" width="520px" append-to-body destroy-on-close align-center>
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="editForm.asset_type" style="width:100%" @change="editFile = null">
            <el-option v-for="t in assetTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="替换文件">
          <el-upload
            :key="editForm.asset_type"
            :auto-upload="false"
            :limit="1"
            :accept="acceptForType(editForm.asset_type)"
            :on-change="onEditFileChange"
          >
            <el-button>选择新文件（{{ extHint(editForm.asset_type) }}，可选）</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="doEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/PageHeader.vue'
import api from '../api'
import { hasPermission } from '../utils/permission'
import { formatTime, formatPreviewContent } from '../utils/format'

const assets = ref([])
const loading = ref(false)
const submitting = ref(false)
const assetTypes = ref([])
const fileRules = ref({})
const keyword = ref('')
const typeFilter = ref('')
const showUpload = ref(false)
const showPreview = ref(false)
const showEdit = ref(false)
const previewData = ref(null)
const uploadFile = ref(null)
const editFile = ref(null)
const editingId = ref(null)

const uploadForm = ref({ name: '', asset_type: '实验报告', description: '' })
const editForm = ref({ name: '', asset_type: '', description: '' })

const canUpload = computed(() => hasPermission('asset:upload'))
const canDownload = computed(() => hasPermission('asset:download'))
const canUpdate = computed(() => hasPermission('asset:update'))
const canDelete = computed(() => hasPermission('asset:delete'))

const filteredAssets = computed(() => {
  let list = assets.value
  if (typeFilter.value) list = list.filter((a) => a.asset_type === typeFilter.value)
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter((a) => a.name.toLowerCase().includes(kw))
  }
  return list
})

function typeColor(t) {
  const map = { '模型资产': 'danger', '数据集': 'warning', 'Prompt模板': 'success', '实验报告': '', '配置文件': 'info', '论文资料': '' }
  return map[t] || ''
}

function extClass(ext) {
  const e = (ext || '').toLowerCase()
  if (e === '.pdf') return 'ext-pdf'
  if (e === '.json') return 'ext-json'
  if (e === '.csv') return 'ext-csv'
  return 'ext-txt'
}

function acceptForType(type) {
  return (fileRules.value[type]?.extensions || []).join(',')
}

function extHint(type) {
  const exts = fileRules.value[type]?.extensions || []
  return exts.length ? exts.join(' / ') : '请先选择类型'
}

function downloadName(row) {
  const ext = row.file_ext || ''
  if (ext && row.name.toLowerCase().endsWith(ext.toLowerCase())) return row.name
  return `${row.name}${ext}`
}

async function load() {
  loading.value = true
  try {
    const [a, types, rules] = await Promise.all([
      api.get('/assets'),
      api.get('/assets/meta/types'),
      api.get('/assets/meta/file-rules'),
    ])
    assets.value = a.data
    assetTypes.value = types.data
    fileRules.value = rules.data
  } finally {
    loading.value = false
  }
}

function onFileChange(file) {
  uploadFile.value = file.raw
  if (!uploadForm.value.name && file.name) {
    uploadForm.value.name = file.name.replace(/\.[^.]+$/, '')
  }
}

function onEditFileChange(file) {
  editFile.value = file.raw
}

async function preview(row) {
  const { data } = await api.get(`/assets/${row.id}/preview`)
  previewData.value = {
    ...data,
    file_ext: row.file_ext,
    content: formatPreviewContent(data.content, row.file_ext),
  }
  showPreview.value = true
}

async function download(row) {
  const res = await api.get(`/assets/${row.id}/download`, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = downloadName(row)
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

function edit(row) {
  editingId.value = row.id
  editForm.value = { name: row.name, asset_type: row.asset_type, description: row.description || '' }
  editFile.value = null
  showEdit.value = true
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除「${row.name}」？`, '确认', { type: 'warning' })
  await api.delete(`/assets/${row.id}`)
  ElMessage.success('删除成功')
  load()
}

async function doUpload() {
  if (!uploadFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  const fd = new FormData()
  fd.append('name', uploadForm.value.name)
  fd.append('asset_type', uploadForm.value.asset_type)
  fd.append('description', uploadForm.value.description)
  fd.append('file', uploadFile.value)
  submitting.value = true
  try {
    await api.post('/assets/upload', fd)
    ElMessage.success('上传成功')
    showUpload.value = false
    uploadForm.value = { name: '', asset_type: '实验报告', description: '' }
    uploadFile.value = null
    load()
  } finally {
    submitting.value = false
  }
}

async function doEdit() {
  submitting.value = true
  try {
    await api.put(`/assets/${editingId.value}`, editForm.value)
    if (editFile.value) {
      const fd = new FormData()
      fd.append('file', editFile.value)
      await api.put(`/assets/${editingId.value}/file`, fd)
    }
    ElMessage.success('修改成功')
    showEdit.value = false
    load()
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  font-family: monospace;
  flex-shrink: 0;
}

.ext-pdf { background: #fef2f2; color: #dc2626; }
.ext-json { background: #eff6ff; color: #2563eb; }
.ext-csv { background: #f0fdf4; color: #16a34a; }
.ext-txt { background: #f8fafc; color: #64748b; }

.filter-count {
  margin-left: auto;
  font-size: 13px;
  color: #94a3b8;
  align-self: center;
}

.upload-icon {
  font-size: 40px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.upload-tip {
  color: #64748b;
  font-size: 14px;
}

.preview-meta {
  margin-bottom: 12px;
}
</style>
