import type { MemoryItem, MemoryOp } from '../api/client';

type Props = {
  ops: MemoryOp[];
  items: MemoryItem[];
};

export function MemoryPanel({ ops, items }: Props) {
  return (
    <section className="panel insight-card">
      <div className="panel-header">
        <div>
          <h2>记忆</h2>
          <p>已存储 {items.length}</p>
        </div>
      </div>
      <div className="memory-grid">
        <div>
          <h3>行动</h3>
          {ops.length === 0 ? <div className="empty-state">无内存操作。</div> : ops.map((op, index) => (
            <div className="mini-row" key={`${op.op}-${op.memory_type}-${index}`}>
              <span>{op.op}</span>
              <strong>{op.memory_type}</strong>
              <small>{op.count ?? op.memory_id ?? ''}</small>
            </div>
          ))}
        </div>
        <div>
          <h3>项目</h3>
          {items.length === 0 ? <div className="empty-state">没有内存项目。</div> : items.slice(0, 6).map((item) => (
            <div className="mini-row" key={item.id}>
              <span>{item.memory_type}</span>
              <strong>{item.summary ?? item.content}</strong>
              <small>{item.importance}</small>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
