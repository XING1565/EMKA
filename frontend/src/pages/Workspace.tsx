import { Activity, BookOpen, Bot, Database, PanelRight, Plus, Sparkles, Wrench } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import {
  type ChatResponse,
  type DocumentItem,
  type MemoryItem,
  type Trace,
  type UploadResult,
  getTrace,
  listDocuments,
  listMemories,
  sendChat,
  uploadDocument
} from '../api/client';
import { ChatPanel } from '../components/ChatPanel';
import { IngestionOpsPanel } from '../components/IngestionOpsPanel';
import { MemoryPanel } from '../components/MemoryPanel';
import { MultimodalUploadPanel } from '../components/MultimodalUploadPanel';
import { ReportPanel } from '../components/ReportPanel';
import { RetrievedDocsPanel } from '../components/RetrievedDocsPanel';
import { ToolCallsPanel } from '../components/ToolCallsPanel';
import { TracePanel } from '../components/TracePanel';
import { formatStatus } from '../utils/display';

const USER_ID = '00000000-0000-0000-0000-000000000101';
const CONVERSATION_ID = '00000000-0000-0000-0000-000000000201';
type SidebarMode = 'knowledge' | 'tools';
type WorkMode = 'auto' | 'search' | 'tools';

export function Workspace() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [lastUpload, setLastUpload] = useState<UploadResult | null>(null);
  const [chat, setChat] = useState<ChatResponse | null>(null);
  const [trace, setTrace] = useState<Trace | null>(null);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [message, setMessage] = useState('');
  const [uploading, setUploading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [chatError, setChatError] = useState<string | null>(null);
  const [sidebarMode, setSidebarMode] = useState<SidebarMode>('knowledge');
  const [workMode, setWorkMode] = useState<WorkMode>('auto');
  const [insightsOpen, setInsightsOpen] = useState(true);

  const retrievedDocs = trace?.retrieved_docs ?? chat?.retrieved_docs ?? [];
  const toolCalls = trace?.tool_calls ?? chat?.tool_calls ?? [];
  const memoryOps = trace?.memory_ops ?? chat?.memory_ops ?? [];
  const ingestionOps = trace?.ingestion_ops ?? chat?.ingestion_ops ?? [];

  const status = useMemo(() => {
    if (chatLoading) return 'running';
    if (trace?.status) return trace.status;
    return 'ready';
  }, [chatLoading, trace]);

  async function refreshDocuments() {
    setDocuments(await listDocuments());
  }

  async function refreshMemories() {
    setMemories(await listMemories(USER_ID));
  }

  useEffect(() => {
    refreshDocuments().catch((error) => setUploadError(error.message));
    refreshMemories().catch(() => undefined);
  }, []);

  async function handleUpload(files: FileList | File[]) {
    const selected = Array.from(files);
    if (selected.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      let latest: UploadResult | null = null;
      for (const file of selected) {
        latest = await uploadDocument(file, USER_ID);
      }
      setLastUpload(latest);
      await refreshDocuments();
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : '上传失败');
    } finally {
      setUploading(false);
    }
  }

  async function handleSend() {
    if (!message.trim()) return;
    setChatLoading(true);
    setChatError(null);
    try {
      const response = await sendChat({
        user_id: USER_ID,
        conversation_id: CONVERSATION_ID,
        message
      });
      setChat(response);
      const loadedTrace = await getTrace(response.trace_id);
      setTrace(loadedTrace);
      await refreshMemories();
    } catch (error) {
      setChatError(error instanceof Error ? error.message : '发送失败');
    } finally {
      setChatLoading(false);
    }
  }

  function handleNewConversation() {
    setMessage('');
    setChat(null);
    setTrace(null);
    setChatError(null);
  }

  return (
    <main className={`workspace ${insightsOpen ? '' : 'insights-collapsed'}`}>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-avatar" aria-hidden="true"><Bot size={26} /></div>
          <div>
            <h1>EMKA 工作区</h1>
            <p>企业多模态知识代理</p>
          </div>
        </div>

        <div className="sidebar-toggles">
          <button
            className={`toggle-pill ${sidebarMode === 'knowledge' ? 'active' : ''}`}
            type="button"
            onClick={() => setSidebarMode('knowledge')}
          >
            <BookOpen size={15} />
            知识库
          </button>
          <button
            className={`toggle-pill ${sidebarMode === 'tools' ? 'active' : ''}`}
            type="button"
            onClick={() => setSidebarMode('tools')}
          >
            <Wrench size={15} />
            工具
          </button>
        </div>

        {sidebarMode === 'knowledge' ? (
          <MultimodalUploadPanel
            documents={documents}
            lastUpload={lastUpload}
            uploading={uploading}
            error={uploadError}
            onUpload={handleUpload}
            onRefresh={() => refreshDocuments().catch((error) => setUploadError(error.message))}
          />
        ) : (
          <section className="sidebar-section tools-section">
            <div className="section-title"><span>可用工具</span></div>
            <div className="tool-option"><Wrench size={15} /><span>资料总结</span></div>
            <div className="tool-option"><BookOpen size={15} /><span>知识检索</span></div>
            <div className="tool-option"><Sparkles size={15} /><span>报告生成</span></div>
          </section>
        )}

        <section className="sidebar-section">
          <div className="section-title">
            <span>最近对话</span>
          </div>
          <div className="soft-empty">暂无对话记录</div>
        </section>

        <button className="new-chat-button" type="button" onClick={handleNewConversation}>
          <Plus size={16} />
          新建对话
        </button>
      </aside>

      <section className="conversation">
        <header className="modebar">
          <div className="modebar-left">
            <button className={`mode-chip ${workMode === 'auto' ? 'active' : ''}`} type="button" onClick={() => setWorkMode('auto')}>
              <Sparkles size={15} />
              智能编排
            </button>
            <button className={`mode-chip ${workMode === 'search' ? 'active' : ''}`} type="button" onClick={() => setWorkMode('search')}>
              <BookOpen size={15} />
              搜索知识库
            </button>
            <button className={`mode-chip ${workMode === 'tools' ? 'active' : ''}`} type="button" onClick={() => setWorkMode('tools')}>
              <Wrench size={15} />
              自动调用工具
            </button>
          </div>
          <div className="modebar-status">
            <span><Database size={15} /> {documents.length} 个文档</span>
            <span><Activity size={15} /> {formatStatus(status)}</span>
          </div>
        </header>

        <ChatPanel
          message={message}
          answer={chat?.answer ?? ''}
          loading={chatLoading}
          onMessageChange={setMessage}
          onSend={handleSend}
        />
        {chatError && <div className="error-box conversation-error">{chatError}</div>}
      </section>

      <aside className="insights">
        <div className="insights-header">
          <div>
            <span className="eyebrow">洞察</span>
            <h2>运行与证据</h2>
          </div>
          <button className="icon-button" type="button" onClick={() => setInsightsOpen((open) => !open)} title={insightsOpen ? '收起洞察' : '展开洞察'}>
            <PanelRight size={18} />
          </button>
        </div>
        <div className="insights-stack">
          <TracePanel chat={chat} trace={trace} />
          <RetrievedDocsPanel docs={retrievedDocs} />
          <ToolCallsPanel calls={toolCalls} />
          <MemoryPanel ops={memoryOps} items={memories} />
          <ReportPanel report={chat?.report ?? null} />
          <IngestionOpsPanel ops={ingestionOps} />
        </div>
      </aside>
    </main>
  );
}

