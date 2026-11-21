import React, { useState, useEffect } from 'react';
import {
  FileText,
  FileSpreadsheet,
  Download,
  Printer,
  ShieldCheck,
  Calendar,
  Layers,
  Award,
} from 'lucide-react';
import { api } from '../services/api';

export default function ReportsView({ summary, onDownloadSamplePdf }) {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDataSource, setSelectedDataSource] = useState('all');

  useEffect(() => {
    loadSamples();
  }, [selectedDataSource]);

  const loadSamples = async () => {
    try {
      setLoading(true);
      const res = await api.getSamples({ perPage: 50, dataSource: selectedDataSource });
      setSamples(res.data || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto' }}>
      {/* Title */}
      <div style={{ marginBottom: '22px' }}>
        <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
          Reports & Export Center
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
          Generate official PDF Soil Health Cards, complete district agronomic reports, and raw CSV data exports.
        </p>
      </div>

      {/* Main Download Cards Grid */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Dataset PDF Report Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <div style={{ padding: '8px', backgroundColor: '#faf3eb', borderRadius: '8px', color: '#7c3f1d' }}>
                <FileText size={22} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0f172a' }}>
                  District Soil Fertility Summary Report (PDF)
                </h3>
                <span className="badge badge-verified">Official Agronomic Document</span>
              </div>
            </div>

            <p style={{ color: '#64748b', fontSize: '0.86rem', lineHeight: 1.45, marginBottom: '16px' }}>
              Comprehensive regional evaluation of Madurai District. Includes overall fertility counts, Rammoorthy & Bajaj nutrient indices, block-wise comparison tables, and TNAU management advisories.
            </p>
          </div>

          <a
            href={api.getDatasetPdfUrl(selectedDataSource)}
            download="soilsense_madurai_dataset_report.pdf"
            className="btn btn-primary"
            style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <Download size={16} /> Download Complete District PDF Report
          </a>
        </div>

        {/* CSV Raw Data Exports Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <div style={{ padding: '8px', backgroundColor: '#dcfce7', borderRadius: '8px', color: '#15803d' }}>
                <FileSpreadsheet size={22} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0f172a' }}>
                  Raw Dataset Exports (CSV)
                </h3>
                <span className="badge badge-verified">Data Analysis Format</span>
              </div>
            </div>

            <p style={{ color: '#64748b', fontSize: '0.86rem', lineHeight: 1.45, marginBottom: '16px' }}>
              Export structured records containing sample IDs, Madurai blocks, measured laboratory parameters (pH, N, P, K), measurement units, and classification ratings.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <a
              href={api.getSamplesCsvUrl(selectedDataSource)}
              download="soil_samples_madurai.csv"
              className="btn btn-secondary"
              style={{ flex: 1, textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              <Download size={15} /> Samples CSV
            </a>
            <a
              href={api.getClassificationCsvUrl(selectedDataSource)}
              download="classification_results_madurai.csv"
              className="btn btn-secondary"
              style={{ flex: 1, textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              <Download size={15} /> Classifications CSV
            </a>
          </div>
        </div>
      </div>

      {/* Individual Sample PDF Download Section */}
      <div className="card">
        <div className="card-title">
          <span>Individual Soil Health Card Reports (PDF)</span>
          <div style={{ width: '180px' }}>
            <select
              className="form-select"
              style={{ padding: '4px 8px', fontSize: '0.8rem' }}
              value={selectedDataSource}
              onChange={(e) => setSelectedDataSource(e.target.value)}
            >
              <option value="all">All Soil Records</option>
              <option value="verified">Verified Lab Only</option>
              <option value="demo">Field Survey Records</option>
            </select>
          </div>
        </div>

        <p style={{ color: '#64748b', fontSize: '0.84rem', marginBottom: '14px' }}>
          Select any sample below to download an official individual Soil Health Card PDF report complete with laboratory test values, TNAU Agritech ratings, and agronomic fertilizer recommendations.
        </p>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Sample ID</th>
                <th>Block / Location</th>
                <th>Date</th>
                <th>Overall Fertility</th>
                <th>Data Source</th>
                <th style={{ textAlign: 'right' }}>Download Report</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '24px' }}>
                    <div className="spinner spinner-primary" style={{ margin: '0 auto' }} />
                  </td>
                </tr>
              ) : samples.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                    No samples available for PDF download.
                  </td>
                </tr>
              ) : (
                samples.map((s) => {
                  const fertClass = s.classification?.fertility_class || 'Pending';
                  const badgeClass =
                    fertClass === 'High' ? 'badge-fertility-high' : fertClass === 'Low' ? 'badge-fertility-low' : 'badge-fertility-medium';
                  const isVerified = s.data_source === 'verified';

                  return (
                    <tr key={s.id}>
                      <td style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1e40af' }}>
                        {s.sample_code}
                      </td>
                      <td>{s.location?.name || 'Melur'}</td>
                      <td>{s.sample_date}</td>
                      <td>
                        <span className={`badge ${badgeClass}`}>{fertClass}</span>
                      </td>
                      <td>
                        <span className={`badge ${isVerified ? 'badge-verified' : 'badge-demo'}`}>
                          {isVerified ? 'Verified Lab' : 'Field Survey'}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-outline-primary btn-sm"
                          onClick={() => onDownloadSamplePdf(s.id, s.sample_code)}
                        >
                          <Download size={14} /> Download Soil Card PDF
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
