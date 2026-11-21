import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  FileDown,
  Trash2,
  Eye,
  PlusCircle,
  AlertCircle,
  CheckCircle,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { api } from '../services/api';
import { MADURAI_BLOCKS } from '../constants/madurai';

export default function SamplesView({ onNavigate, onDownloadSamplePdf }) {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(true);
  const [meta, setMeta] = useState({ page: 1, total: 0, total_pages: 1 });
  const [search, setSearch] = useState('');
  const [locationId, setLocationId] = useState('');
  const [fertilityClass, setFertilityClass] = useState('all');
  const [dataSource, setDataSource] = useState('all');
  const [locations, setLocations] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [error, setError] = useState(null);

  const fetchSamples = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getSamples({
        page,
        perPage: 15,
        search,
        locationId,
        fertilityClass,
        dataSource,
      });
      setSamples(res.data);
      setMeta(res.meta);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    api.getLocations().then((res) => setLocations(res.data || [])).catch(() => {});
  }, []);

  useEffect(() => {
    fetchSamples(1);
  }, [locationId, fertilityClass, dataSource]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchSamples(1);
  };

  const handleDelete = async (id, code) => {
    if (!window.confirm(`Are you sure you want to delete sample ${code}?`)) return;
    try {
      await api.deleteSample(id);
      fetchSamples(meta.page);
    } catch (err) {
      alert(`Could not delete sample: ${err.message}`);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '22px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
            Madurai District Soil Samples Explorer
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Search, filter, and inspect verified laboratory and field soil test records.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => onNavigate('entry')}>
          <PlusCircle size={16} /> Add Soil Sample
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search Input */}
          <div style={{ flex: 1, minWidth: '220px', position: 'relative' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Search by Sample Code, Village, Collector…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '34px' }}
            />
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '11px', top: '50%', transform: 'translateY(-50%)' }} />
          </div>

          {/* Block / Location Filter */}
          <div style={{ width: '190px' }}>
            <select className="form-select" value={locationId} onChange={(e) => setLocationId(e.target.value)}>
              <option value="">All Locations / Blocks</option>
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.name}
                </option>
              ))}
            </select>
          </div>

          {/* Fertility Class Filter */}
          <div style={{ width: '160px' }}>
            <select className="form-select" value={fertilityClass} onChange={(e) => setFertilityClass(e.target.value)}>
              <option value="all">All Fertility Classes</option>
              <option value="High">High Fertility</option>
              <option value="Medium">Medium Fertility</option>
              <option value="Low">Low Fertility</option>
            </select>
          </div>

          {/* Data Source Filter */}
          <div style={{ width: '150px' }}>
            <select className="form-select" value={dataSource} onChange={(e) => setDataSource(e.target.value)}>
              <option value="all">All Data Sources</option>
              <option value="verified">Verified Lab</option>
              <option value="demo">Field Survey</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary">
            Filter
          </button>
        </form>
      </div>

      {error && (
        <div className="alert alert-danger">
          <AlertCircle size={18} />
          <div>{error}</div>
        </div>
      )}

      {/* Samples Table */}
      <div className="card" style={{ padding: '0' }}>
        <div className="table-container" style={{ border: 'none' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Sample ID</th>
                <th>Block / Taluk</th>
                <th>Village</th>
                <th>Date</th>
                <th>pH</th>
                <th>Nitrogen (N)</th>
                <th>Phosphorus (P)</th>
                <th>Potassium (K)</th>
                <th>Overall Fertility</th>
                <th>Source</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={11} style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="spinner spinner-primary" style={{ margin: '0 auto 10px' }} />
                    <p style={{ color: '#64748b' }}>Loading records…</p>
                  </td>
                </tr>
              ) : samples.length === 0 ? (
                <tr>
                  <td colSpan={11} style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                    No soil samples match the specified criteria.
                  </td>
                </tr>
              ) : (
                samples.map((s) => {
                  const paramMap = {};
                  s.parameter_values?.forEach((pv) => {
                    paramMap[pv.parameter_code] = pv.value;
                  });
                  const fertClass = s.classification?.fertility_class || 'Pending';
                  const badgeClass =
                    fertClass === 'High' ? 'badge-fertility-high' : fertClass === 'Low' ? 'badge-fertility-low' : 'badge-fertility-medium';
                  const isVerified = s.data_source === 'verified';

                  return (
                    <tr key={s.id}>
                      <td style={{ fontWeight: 700, fontFamily: 'monospace', color: '#1e40af' }}>{s.sample_code}</td>
                      <td>
                        <span style={{ fontWeight: 600 }}>{s.location?.taluk_block || s.location?.name || 'Melur'}</span>
                      </td>
                      <td style={{ color: '#475569' }}>{s.location?.village || s.location?.name || '-'}</td>
                      <td>{s.sample_date}</td>
                      <td>
                        <strong>{paramMap.ph !== undefined ? paramMap.ph.toFixed(2) : '-'}</strong>
                      </td>
                      <td>{paramMap.nitrogen !== undefined ? `${paramMap.nitrogen.toFixed(0)} kg/ha` : '-'}</td>
                      <td>{paramMap.phosphorus !== undefined ? `${paramMap.phosphorus.toFixed(1)} kg/ha` : '-'}</td>
                      <td>{paramMap.potassium !== undefined ? `${paramMap.potassium.toFixed(0)} kg/ha` : '-'}</td>
                      <td>
                        <span className={`badge ${badgeClass}`}>{fertClass}</span>
                      </td>
                      <td>
                        <span className={`badge ${isVerified ? 'badge-verified' : 'badge-demo'}`}>
                          {isVerified ? 'Verified Lab' : 'Field Survey'}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: '6px' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            title="View details"
                            onClick={() => setSelectedSample(s)}
                          >
                            <Eye size={14} />
                          </button>
                          <button
                            className="btn btn-outline-primary btn-sm"
                            title="Download PDF Soil Health Card"
                            onClick={() => onDownloadSamplePdf(s.id, s.sample_code)}
                          >
                            <FileDown size={14} />
                          </button>
                          <button
                            className="btn btn-danger-outline btn-sm"
                            title="Delete sample"
                            onClick={() => handleDelete(s.id, s.sample_code)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
          <div style={{ color: '#64748b' }}>
            Showing <strong>{samples.length}</strong> of <strong>{meta.total}</strong> samples
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className="btn btn-secondary btn-sm"
              disabled={meta.page <= 1}
              onClick={() => fetchSamples(meta.page - 1)}
            >
              <ChevronLeft size={14} /> Prev
            </button>
            <span style={{ color: '#475569', fontWeight: 600 }}>
              Page {meta.page} of {meta.total_pages}
            </span>
            <button
              className="btn btn-secondary btn-sm"
              disabled={meta.page >= meta.total_pages}
              onClick={() => fetchSamples(meta.page + 1)}
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Sample Details Modal */}
      {selectedSample && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 50,
            padding: '20px',
          }}
        >
          <div className="card" style={{ width: '100%', maxWidth: '640px', maxHeight: '90vh', overflowY: 'auto', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1e40af' }}>
                  Soil Sample: {selectedSample.sample_code}
                </h3>
                <p style={{ color: '#64748b', fontSize: '0.82rem' }}>
                  Madurai District, Tamil Nadu • Conforms to TNAU Rating Standards
                </p>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedSample(null)}
                style={{ padding: '6px' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Metadata Box */}
            <div style={{ backgroundColor: '#faf5ef', padding: '14px', borderRadius: '8px', border: '1px solid #ebdcd0', marginBottom: '18px' }}>
              <div className="grid-2" style={{ gap: '10px', fontSize: '0.85rem' }}>
                <div>
                  <strong>Location / Block:</strong> {selectedSample.location?.name || 'Melur'}
                </div>
                <div>
                  <strong>Sampling Date:</strong> {selectedSample.sample_date}
                </div>
                <div>
                  <strong>Sampling Depth:</strong> {selectedSample.depth_cm || 20} cm
                </div>
                <div>
                  <strong>Land Use:</strong> {selectedSample.land_use || 'Agricultural'}
                </div>
                <div>
                  <strong>Collector:</strong> {selectedSample.collector_name || 'Field Officer'}
                </div>
                <div>
                  <strong>Data Integrity:</strong>{' '}
                  <span className={`badge ${selectedSample.data_source === 'verified' ? 'badge-verified' : 'badge-demo'}`}>
                    {selectedSample.data_source === 'verified' ? 'Verified Lab Data' : 'Field Survey Assessment'}
                  </span>
                </div>
              </div>
            </div>

            {/* Overall Fertility Status */}
            <div style={{ padding: '14px', borderRadius: '8px', backgroundColor: '#faf3eb', border: '1px solid #ebdcd0', marginBottom: '18px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#7c3f1d', textTransform: 'uppercase' }}>
                Overall Fertility Grouping
              </div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#7c3f1d', marginTop: '2px' }}>
                {selectedSample.classification?.fertility_class || 'Pending'} Fertility
              </div>
              <div style={{ fontSize: '0.85rem', color: '#6e5d52', marginTop: '4px' }}>
                {selectedSample.classification?.overall_status}
              </div>
            </div>

            {/* Parameter Values Table */}
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '8px' }}>Parameter Ratings</h4>
            <div className="table-container" style={{ marginBottom: '20px' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                    <th>Unit</th>
                    <th>Method</th>
                    <th>TNAU Rating</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedSample.parameter_values?.map((pv) => {
                    let rating = '-';
                    const cr = selectedSample.classification;
                    if (cr) {
                      if (pv.parameter_code === 'ph') rating = cr.ph_class;
                      else if (pv.parameter_code === 'nitrogen') rating = cr.n_class;
                      else if (pv.parameter_code === 'phosphorus') rating = cr.p_class;
                      else if (pv.parameter_code === 'potassium') rating = cr.k_class;
                    }
                    return (
                      <tr key={pv.parameter_code}>
                        <td style={{ fontWeight: 600 }}>{pv.display_name || pv.parameter_code}</td>
                        <td>{pv.value}</td>
                        <td>{pv.unit}</td>
                        <td style={{ fontSize: '0.78rem', color: '#64748b' }}>{pv.test_method}</td>
                        <td style={{ fontWeight: 700, textTransform: 'capitalize' }}>{rating}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                className="btn btn-primary"
                onClick={() => onDownloadSamplePdf(selectedSample.id, selectedSample.sample_code)}
              >
                <FileDown size={16} /> Download Official PDF Report
              </button>
              <button className="btn btn-secondary" onClick={() => setSelectedSample(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
