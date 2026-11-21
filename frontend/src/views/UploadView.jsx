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
} from 'lucide-react';
import { api } from '../services/api';

export default function UploadView({ onNavigate }) {
  const [file, setFile] = useState(null);
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
      <div className="card" style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#faf5ef', border: '1px solid #ebdcd0' }}>
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
        <div className="alert alert-danger">
          <AlertCircle size={18} />
          <div>{error}</div>
        </div>
      )}

      {/* Upload Box */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">Upload Dataset File</div>

        <div
          style={{
            border: '2px dashed #cbd5e1',
            borderRadius: '12px',
            padding: '36px 20px',
            textAlign: 'center',
            backgroundColor: file ? '#f0fdf4' : '#fafafa',
            cursor: 'pointer',
            marginBottom: '20px',
            transition: 'background-color 0.2s',
          }}
          onClick={() => document.getElementById('csv-file-input').click()}
        >
          <input
            id="csv-file-input"
            type="file"
            accept=".csv"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <div style={{ display: 'flex', justifyContent: 'center', color: file ? '#15803d' : '#1e40af', marginBottom: '12px' }}>
            <UploadCloud size={40} />
          </div>
          {file ? (
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: '#15803d' }}>
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>
                Click to choose a different CSV file
              </div>
            </div>
          ) : (
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f172a' }}>
                Click to browse or drop your CSV file here
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>
                Maximum size: 10MB • Must be formatted as UTF-8 CSV
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
            Validate Only
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

      {/* Ingestion Success Banner */}
      {uploadSuccess && (
        <div className="alert alert-success" style={{ marginBottom: '24px' }}>
          <CheckCircle2 size={20} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
              Dataset Ingestion Complete!
            </div>
            <p style={{ marginTop: '2px' }}>
              Batch ID: <code>{uploadSuccess.batch.uuid}</code> • Successfully ingested{' '}
              <strong>{uploadSuccess.batch.valid_rows}</strong> valid soil samples.
            </p>
            <button
              className="btn btn-primary btn-sm"
              style={{ marginTop: '10px' }}
              onClick={() => onNavigate('samples')}
            >
              View Samples in Explorer <ArrowRight size={14} />
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
                Validation Errors (Rows will be skipped or rejected)
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
                        <td style={{ fontFamily: 'monospace', color: '#1e40af' }}>{err.column}</td>
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
                Validation Warnings (Non-fatal)
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
                        <td style={{ fontFamily: 'monospace', color: '#475569' }}>{w.column}</td>
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
