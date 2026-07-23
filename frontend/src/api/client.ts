export type DocumentItem = {
  id: string;
  title: string;
  doc_type: string;
  modality: 'text' | 'table' | 'image';
  summary: string | null;
};

export type UploadResult = {
  document_id: string;
  title: string;
  modality: 'text' | 'table' | 'image';
  parser: string;
  chunk_count: number;
  indexed: boolean;
};

export type RetrievedDoc = {
  document_id: string;
  title: string;
  modality: string;
  score: number;
  citation: string;
  snippet: string;
  row_range?: string;
  ocr_confidence?: number;
};

export type ToolCall = {
  id?: string;
  trace_id?: string;
  tool_name: string;
  params: Record<string, unknown>;
  result: Record<string, unknown>;
  success: boolean;
  error?: string | null;
  latency_ms?: number | null;
};

export type MemoryOp = {
  op: string;
  memory_type: string;
  count?: number;
  memory_id?: string;
};

export type MemoryItem = {
  id: string;
  memory_type: string;
  content: string;
  summary: string | null;
  importance: number;
  metadata: Record<string, unknown>;
};

export type ChatResponse = {
  answer: string;
  report: { title: string; content_md: string } | null;
  trace_id: string;
  route: Record<string, unknown>;
  plan: Array<Record<string, unknown>>;
  retrieved_docs: RetrievedDoc[];
  tool_calls: ToolCall[];
  memory_ops: MemoryOp[];
  ingestion_ops: Array<Record<string, unknown>>;
};

export type Trace = {
  id: string;
  intent: string | null;
  route_confidence: number | null;
  route: Record<string, unknown>;
  plan: Array<Record<string, unknown>>;
  retrieved_docs: RetrievedDoc[];
  tool_calls: ToolCall[];
  memory_ops: MemoryOp[];
  ingestion_ops: Array<Record<string, unknown>>;
  latency_ms: number | null;
  status: string;
  error: string | null;
};

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function uploadDocument(file: File, userId: string, docType = 'general'): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);
  formData.append('doc_type', docType);
  return requestJson<UploadResult>('/api/v1/documents/upload', {
    method: 'POST',
    body: formData
  });
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const data = await requestJson<{ items: DocumentItem[] }>('/api/v1/documents');
  return data.items;
}

export async function sendChat(input: {
  user_id: string;
  conversation_id: string;
  message: string;
  mode?: string;
}): Promise<ChatResponse> {
  return requestJson<ChatResponse>('/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...input, mode: input.mode ?? 'auto' })
  });
}

export async function getTrace(traceId: string): Promise<Trace> {
  return requestJson<Trace>(`/api/v1/traces/${traceId}`);
}

export async function listMemories(userId: string): Promise<MemoryItem[]> {
  const data = await requestJson<{ items: MemoryItem[] }>(`/api/v1/memories?user_id=${encodeURIComponent(userId)}`);
  return data.items;
}
