import { Bot, Send, Sparkles } from 'lucide-react';

type Props = {
  message: string;
  answer: string;
  loading: boolean;
  onMessageChange: (value: string) => void;
  onSend: () => void;
};

export function ChatPanel({ message, answer, loading, onMessageChange, onSend }: Props) {
  const canSend = Boolean(message.trim()) && !loading;

  return (
    <section className="chat-panel">
      <div className="chat-stage">
        {answer ? (
          <article className="answer-card">
            <span className="answer-avatar" aria-hidden="true"><Bot size={24} /></span>
            <div>
              <h2>回答</h2>
              <p>{answer}</p>
            </div>
          </article>
        ) : (
          <div className="welcome-state">
            <Sparkles size={36} />
            <h2>你好，有什么我能帮忙的吗？</h2>
            <p>开启知识库可搜索您上传的文件；选择工具后，我会自动推理并调用完成它们的任务。</p>
          </div>
        )}
      </div>

      <div className="composer-shell">
        <div className="composer">
          <textarea
            value={message}
            onChange={(event) => onMessageChange(event.target.value)}
            placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
            rows={1}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                if (canSend) onSend();
              }
            }}
          />
          <button className="send-button" type="button" onClick={onSend} disabled={!canSend} title="发送">
            {loading ? <span className="loading-dot" /> : <Send size={18} />}
          </button>
        </div>
        <div className="prompt-chips">
          <button type="button" onClick={() => onMessageChange('请总结我上传的资料')}>总结资料</button>
          <button type="button" onClick={() => onMessageChange('请基于知识库回答关键问题')}>知识问答</button>
          <button type="button" onClick={() => onMessageChange('请生成一份 Markdown 报告')}>报告生成</button>
          <button type="button" onClick={() => onMessageChange('请列出可引用的证据')}>引用证据</button>
        </div>
      </div>
    </section>
  );
}


