import type { RetrievedDoc } from '../api/client';
import { formatModality } from '../utils/display';

type Props = {
  docs: RetrievedDoc[];
};

export function RetrievedDocsPanel({ docs }: Props) {
  return (
    <section className="panel insight-card">
      <div className="panel-header">
        <div>
          <h2>检索文档</h2>
          <p>{docs.length} 次引用</p>
        </div>
      </div>
      <div className="stack-list">
        {docs.length === 0 ? (
          <div className="empty-state">未检索到相关证据。</div>
        ) : (
          docs.map((doc, index) => (
            <article className="evidence-row" key={`${doc.document_id}-${index}`}>
              <div className="row-title">
                <strong>{doc.title}</strong>
                <span className={`pill ${doc.modality}`}>{formatModality(doc.modality)}</span>
              </div>
              <p>{doc.citation}</p>
              <small>{doc.snippet}</small>
              <div className="meta-grid">
                <span>相关度 {doc.score.toFixed(3)}</span>
                {doc.row_range && <span>行 {doc.row_range}</span>}
                {doc.ocr_confidence !== undefined && <span>OCR {doc.ocr_confidence}</span>}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
