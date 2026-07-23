import { FileUp, RefreshCcw, UploadCloud } from 'lucide-react';
import type { DocumentItem, UploadResult } from '../api/client';
import { formatDocType, formatIndexed, formatModality } from '../utils/display';

type Props = {
  documents: DocumentItem[];
  lastUpload: UploadResult | null;
  uploading: boolean;
  error: string | null;
  onUpload: (files: FileList | File[]) => void;
  onRefresh: () => void;
};

export function MultimodalUploadPanel({ documents, lastUpload, uploading, error, onUpload, onRefresh }: Props) {
  return (
    <section className="upload-panel sidebar-section">
      <div className="panel-header">
        <div>
          <h2>私人黑洞</h2>
          <p>文本、表格、图像</p>
        </div>
        <button className="icon-button" onClick={onRefresh} title="刷新文档" type="button">
          <RefreshCcw size={16} />
        </button>
      </div>

      <label
        className="drop-zone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          onUpload(event.dataTransfer.files);
        }}
      >
        <UploadCloud size={24} />
        <strong>{uploading ? '正在上传...' : '上传个人文件'}</strong>
        <span>点击或拖拽到此处</span>
        <input
          type="file"
          multiple
          accept=".txt,.md,.pdf,.docx,.csv,.xlsx,.png,.jpg,.jpeg"
          onChange={(event) => {
            if (event.target.files) {
              onUpload(event.target.files);
              event.target.value = '';
            }
          }}
        />
      </label>

      {error && <div className="error-box">{error}</div>}

      {lastUpload && (
        <div className="result-card">
          <div className="row-title">
            <FileUp size={15} />
            <strong>{lastUpload.title}</strong>
          </div>
          <div className="meta-grid">
            <span>{formatModality(lastUpload.modality)}</span>
            <span>{lastUpload.parser}</span>
            <span>{lastUpload.chunk_count} 个切片</span>
            <span>{formatIndexed(lastUpload.indexed)}</span>
          </div>
        </div>
      )}

      <div className="section-title document-title">
        <span>本地文档库</span>
        <small>{documents.length} 个文档</small>
      </div>
      <div className="document-list">
        {documents.length === 0 ? (
          <div className="soft-empty">暂无本地文档。上传后会出现在这里。</div>
        ) : (
          documents.map((document) => (
            <article className="document-row" key={document.id}>
              <div>
                <strong>{document.title}</strong>
                <p>{formatDocType(document.doc_type)}</p>
              </div>
              <span className={`pill ${document.modality}`}>{formatModality(document.modality)}</span>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
