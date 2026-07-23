export function formatStatus(status?: string | null) {
  const value = status ?? 'waiting';
  const labels: Record<string, string> = {
    ready: '准备好',
    running: '运行中',
    success: '成功',
    failed: '失败',
    waiting: '等待中',
    completed: '已完成',
    error: '异常'
  };
  return labels[value] ?? value;
}

export function formatModality(modality?: string | null) {
  const value = modality ?? 'text';
  const labels: Record<string, string> = {
    text: '文本',
    table: '表格',
    image: '图像'
  };
  return labels[value] ?? value;
}

export function formatDocType(docType?: string | null) {
  const value = docType ?? 'general';
  const labels: Record<string, string> = {
    general: '通用资料'
  };
  return labels[value] ?? value;
}

export function formatIndexed(indexed: boolean) {
  return indexed ? '已索引' : '未索引';
}
