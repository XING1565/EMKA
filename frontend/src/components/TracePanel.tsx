import type { ChatResponse, Trace } from '../api/client';
import { formatStatus } from '../utils/display';

type Props = {
  chat: ChatResponse | null;
  trace: Trace | null;
};

export function TracePanel({ chat, trace }: Props) {
  const route = trace?.route ?? chat?.route;
  const plan = trace?.plan ?? chat?.plan ?? [];
  return (
    <section className="panel insight-card">
      <div className="panel-header">
        <div>
          <h2>执行轨迹</h2>
          <p>{formatStatus(trace?.status ?? 'waiting')}</p>
        </div>
        {trace?.latency_ms !== null && trace?.latency_ms !== undefined && <span className="metric">{trace.latency_ms} ms</span>}
      </div>
      {route ? (
        <div className="trace-stack">
          <div className="kv"><span>意图</span><strong>{String(route.intent ?? trace?.intent ?? '-')}</strong></div>
          <div className="kv"><span>置信度</span><strong>{String(route.confidence ?? trace?.route_confidence ?? '-')}</strong></div>
          <div className="plan-list">
            {plan.map((step, index) => (
              <div className="plan-step" key={`${String(step.id ?? index)}-${index}`}>
                <span>{index + 1}</span>
                <strong>{String(step.tool ?? step.action ?? '步骤')}</strong>
                <p>{String(step.action ?? '')}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state">等待运行后显示轨迹。</div>
      )}
    </section>
  );
}
