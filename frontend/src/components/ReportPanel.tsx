type Props = {
  report: { title: string; content_md: string } | null;
};

export function ReportPanel({ report }: Props) {
  return (
    <section className="panel report-panel insight-card">
      <div className="panel-header">
        <div>
          <h2>报告</h2>
          <p>Markdown 输出</p>
        </div>
      </div>
      {report ? (
        <pre>{report.content_md}</pre>
      ) : (
        <div className="empty-state">未生成报告。</div>
      )}
    </section>
  );
}
