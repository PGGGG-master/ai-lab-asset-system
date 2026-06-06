export function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

export function formatPreviewContent(content, fileExt) {
  if (!content) return ''
  const ext = (fileExt || '').toLowerCase()
  if (ext === '.json') {
    try {
      return JSON.stringify(JSON.parse(content), null, 2)
    } catch {
      return content
    }
  }
  return content
}
