import type { ToolCall } from '../api/client';

type Props = {
  calls: ToolCall[];
};

export function ToolCallsPanel({ calls }: Props) {
  return (
    <section className="panel insight-card">
      <div className="panel-header">
        <div>
          <h2>工具调用</h2>
          <p>{calls.length} 次调用</p>
        </div>
      </div>
      <div className="stack-list">
        {calls.length === 0 ? (
          <div className="empty-state">无需工具调用。</div>
        ) : (
          calls.map((call, index) => (
            <article className="tool-row" key={`${call.tool_name}-${index}`}>
              <div className="row-title">
                <strong>{call.tool_name}</strong>
                <span className={call.success ? 'status-ok' : 'status-fail'}>{call.success ? '成功' : '失败'}</span>
              </div>
              <small>{call.latency_ms ?? 0} ms</small>
              {call.error && <p className="error-text">{call.error}</p>}
              <pre>{JSON.stringify(call.result, null, 2)}</pre>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
