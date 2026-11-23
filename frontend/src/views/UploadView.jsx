import React, { useState } from 'react';
import {
  UploadCloud,
  FileSpreadsheet,
  Download,
  AlertCircle,
  CheckCircle2,
  FileCheck,
  AlertTriangle,
  ArrowRight,
  Copy,
  XCircle,
} from 'lucide-react';
import { api } from '../services/api';

export default function UploadView({ onNavigate }) {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dataSource, setDataSource] = useState('verified');
  const [locationName, setLocationName] = useState('');
  const [validating, setValidating] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [validationReport, setValidationReport] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setValidationReport(null);
      setUploadSuccess(null);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setValidationReport(null);
        setUploadSuccess(null);
        setError(null);
      } else {
        setError('Please drop a valid .csv file.');
      }
    }
  };

  const handleValidateOnly = async () => {
    if (!file) return;
    try {
      setValidating(true);
      setError(null);
      const report = await api.validateCSV(file);
      setValidationReport(report);
    } catch (err) {
      setError(err.message);
    } finally {
      setValidating(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      setUploading(true);
      setError(null);
      const res = await api.uploadCSV(file, dataSource, locationName);
      setUploadSuccess(res);
      setValidationReport(res.validation_report);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const summary = uploadSuccess?.summary || {
    total_rows: uploadSuccess?.batch?.total_rows || 0,
    successful_records: uploadSuccess?.batch?.valid_rows || 0,
    duplicate_records: 0,
    failed_records: uploadSuccess?.batch?.error_rows || 0,
  };

  return (
    <div style={{ maxWidth: '920px', margin: '0 auto' }}>
      {/* Title */}
      <div style={{ marginBottom: '22px' }}>
        <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
          Batch Soil Sample Ingestion (CSV)
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
          Upload soil sample laboratory datasets for Madurai District. All records are validated against Madurai geography and standard agricultural thresholds.
        </p>
      </div>

      {/* Template Download Card */}
      <div
        className="card"
        style={{
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#faf5ef',
          border: '1px solid #ebdcd0',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ padding: '10px', backgroundColor: '#faf3eb', borderRadius: '10px', color: '#7c3f1d' }}>
            <FileSpreadsheet size={24} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>
              Standard Soil Sample CSV Template
            </div>
            <div style={{ fontSize: '0.82rem', color: '#64748b' }}>
              Includes required headers: sample_code, district, location_name, sample_date, ph, nitrogen_kg_ha, phosphorus_kg_ha, potassium_kg_ha.
            </div>
          </div>
        </div>
        <a
          href={api.getTemplateDownloadUrl()}
          download="soil_sample_upload_template.csv"
          className="btn btn-primary btn-sm"
          style={{ textDecoration: 'none' }}
        >
          <Download size={14} /> Download CSV Template
        </a>
      </div>

      {error && (
        <div className="alert alert-danger" style={{ marginBottom: '20px' }}>
          <AlertCircle size={18} />
          <div>{error}</div>
        </div>
      )}

      {/* Upload Box */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">Upload Dataset File</div>

        <div
          style={{
            border: isDragging ? '2px dashed #1e40af' : '2px dashed #cbd5e1',
            borderRadius: '12px',
            padding: '36px 20px',
            textAlign: 'center',
            backgroundColor: isDragging ? '#eff6ff' : file ? '#f0fdf4' : '#fafafa',
            cursor: 'pointer',
            marginBottom: '20px',
            transition: 'all 0.2s ease',
          }}
          onClick={() => document.getElementById('csv-file-input').click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            id="csv-file-input"
            type="file"
            accept=".csv"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              color: file ? '#15803d' : '#1e40af',
              marginBottom: '12px',
            }}
          >
            <UploadCloud size={44} />
          </div>
          {file ? (
            <div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#15803d' }}>
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>
                Click or drag another file to replace
              </div>
            </div>
          ) : (
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f172a' }}>
                Drag and drop your CSV file here, or click to browse
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>
                Supports standard comma-separated soil sample datasets • Max 10MB
              </div>
            </div>
          )}
        </div>

        {/* Options */}
        <div className="grid-2" style={{ marginBottom: '20px' }}>
          <div className="form-group">
            <label className="form-label">Data Source Tag</label>
            <select
              className="form-select"
              value={dataSource}
              onChange={(e) => setDataSource(e.target.value)}
            >
              <option value="verified">Verified (Official Soil Testing Lab Data)</option>
              <option value="demo">Field Survey Assessment Records</option>
            </select>
            <div className="form-helper">
              Categorizes certified laboratory soil tests and field sampling records.
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Default Block / Location Override (Optional)</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Melur (leave empty if specified in CSV)"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
            />
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            type="button"
            className="btn btn-secondary"
            disabled={!file || validating || uploading}
            onClick={handleValidateOnly}
          >
            {validating ? <span className="spinner spinner-primary" /> : <FileCheck size={16} />}
            Validate CSV
          </button>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!file || validating || uploading}
            onClick={handleUpload}
          >
            {uploading ? <span className="spinner" /> : <UploadCloud size={16} />}
            Upload and Ingest
          </button>
        </div>
      </div>

      {/* Ingestion Result Summary Banner */}
      {uploadSuccess && (
        <div
          className="card"
          style={{
            marginBottom: '24px',
            backgroundColor: summary.successful_records > 0 ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${summary.successful_records > 0 ? '#bbf7d0' : '#fecaca'}`,
            padding: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            {summary.successful_records > 0 ? (
              <CheckCircle2 size={26} color="#15803d" />
            ) : (
              <XCircle size={26} color="#dc2626" />
            )}
            <div>
              <h3
                style={{
                  fontSize: '1.15rem',
                  fontWeight: 800,
                  color: summary.successful_records > 0 ? '#15803d' : '#dc2626',
                  margin: 0,
                }}
              >
                {summary.successful_records > 0 ? 'Dataset Ingestion Complete!' : 'Dataset Ingestion Failed'}
              </h3>
              <p style={{ margin: '3px 0 0', fontSize: '0.85rem', color: '#475569' }}>
                Batch UUID: <code style={{ fontWeight: 600 }}>{uploadSuccess.batch.uuid}</code>
              </p>
            </div>
          </div>

          {/* Record Ingestion Statistics Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
              gap: '12px',
              marginBottom: '18px',
            }}
          >
            <div
              style={{
                padding: '12px',
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '0.74rem', color: '#64748b', fontWeight: 600 }}>TOTAL ROWS</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f172a' }}>
                {summary.total_rows}
              </div>
            </div>

            <div
              style={{
                padding: '12px',
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #bbf7d0',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '0.74rem', color: '#15803d', fontWeight: 600 }}>SAVED TO DB</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#15803d' }}>
                {summary.successful_records}
              </div>
            </div>

            <div
              style={{
                padding: '12px',
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #fef08a',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '0.74rem', color: '#b45309', fontWeight: 600 }}>DUPLICATES SKIPPED</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#b45309' }}>
                {summary.duplicate_records}
              </div>
            </div>

            <div
              style={{
                padding: '12px',
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                border: '1px solid #fecaca',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '0.74rem', color: '#dc2626', fontWeight: 600 }}>ERRORS / FAILED</div>
              <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#dc2626' }}>
                {summary.failed_records}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button
              className="btn btn-primary"
              onClick={() => onNavigate('samples')}
            >
              View Samples in Explorer <ArrowRight size={15} />
            </button>
          </div>
        </div>
      )}

      {/* Validation Report View */}
      {validationReport && (
        <div className="card">
          <div className="card-title">
            <span>Validation Report Summary</span>
            <span
              className={`badge ${
                validationReport.error_rows === 0 ? 'badge-verified' : 'badge-fertility-low'
              }`}
            >
              {validationReport.error_rows === 0 ? 'All Rows Valid' : `${validationReport.error_rows} Issues Found`}
            </span>
          </div>

          <div className="grid-3" style={{ marginBottom: '16px' }}>
            <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>TOTAL ROWS</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{validationReport.total_rows}</div>
            </div>
            <div style={{ padding: '12px', backgroundColor: '#f0fdf4', borderRadius: '8px', border: '1px solid #bbf7d0', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: '#15803d' }}>VALID ROWS</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#15803d' }}>{validationReport.valid_rows}</div>
            </div>
            <div style={{ padding: '12px', backgroundColor: '#fef2f2', borderRadius: '8px', border: '1px solid #fecaca', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: '#dc2626' }}>ERROR ROWS</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#dc2626' }}>{validationReport.error_rows}</div>
            </div>
          </div>

          {/* Errors List */}
          {validationReport.errors && validationReport.errors.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#dc2626', marginBottom: '8px' }}>
                Validation Errors (Rows rejected or skipped)
              </h4>
              <div className="table-container" style={{ marginBottom: '16px' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th style={{ width: '80px' }}>Row</th>
                      <th style={{ width: '130px' }}>Column</th>
                      <th>Issue Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {validationReport.errors.map((err, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: 600 }}>{err.row !== null ? `Row ${err.row}` : 'Header'}</td>
                        <td style={{ fontFamily: 'monospace', color: '#1e40af' }}>{err.column || 'General'}</td>
                        <td style={{ color: '#dc2626' }}>{err.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Warnings List */}
          {validationReport.warnings && validationReport.warnings.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#d97706', marginBottom: '8px' }}>
                Validation Warnings & Notices (Duplicate / Non-fatal)
              </h4>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th style={{ width: '80px' }}>Row</th>
                      <th style={{ width: '130px' }}>Column</th>
                      <th>Notice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {validationReport.warnings.map((w, i) => (
                      <tr key={i}>
                        <td style={{ fontWeight: 600 }}>{w.row !== null ? `Row ${w.row}` : 'File'}</td>
                        <td style={{ fontFamily: 'monospace', color: '#475569' }}>{w.column || 'General'}</td>
                        <td style={{ color: '#92400e' }}>{w.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
