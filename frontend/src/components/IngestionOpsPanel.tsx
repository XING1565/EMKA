type Props = {
  ops: Array<Record<string, unknown>>;
};

export function IngestionOpsPanel({ ops }: Props) {
  return (
    <section className="panel insight-card">
      <div className="panel-header">
        <div>
          <h2>提取操作</h2>
          <p>{ops.length} 起事件</p>
        </div>
      </div>
      {ops.length === 0 ? (
        <div className="empty-state">最新跟踪记录中没有数据提取操作。</div>
      ) : (
        <pre>{JSON.stringify(ops, null, 2)}</pre>
      )}
    </section>
  );
}
