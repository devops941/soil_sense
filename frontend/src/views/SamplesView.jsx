import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  FileDown,
  Trash2,
  Eye,
  Pencil,
  PlusCircle,
  AlertCircle,
  CheckCircle,
  X,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Sparkles,
  MapPin,
  Calendar,
} from 'lucide-react';
import { api } from '../services/api';
import { MADURAI_BLOCKS, MADURAI_DISTRICT, COMMON_CROPS, TESTING_METHODS } from '../constants/madurai';

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
  const [editingSample, setEditingSample] = useState(null);
  const [editFormData, setEditFormData] = useState(null);
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
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
      setSamples(res.data || []);
      setMeta(res.meta || { page: 1, total: 0, total_pages: 1 });
    } catch (err) {
      setError(err.message || 'Failed to fetch soil sample records.');
      setSamples([]);
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

  const handleResetFilters = () => {
    setSearch('');
    setLocationId('');
    setFertilityClass('all');
    setDataSource('all');
  };

  const handleDelete = async (id, code) => {
    if (!window.confirm(`Are you sure you want to delete sample ${code}?`)) return;
    try {
      await api.deleteSample(id);
      setSuccessMessage(`Sample ${code} successfully deleted.`);
      fetchSamples(meta.page);
    } catch (err) {
      setError(`Could not delete sample: ${err.message}`);
    }
  };

  // Open Edit Modal and prefill form data
  const handleOpenEdit = (sample) => {
    const paramMap = {};
    const methodMap = {};
    sample.parameter_values?.forEach((pv) => {
      paramMap[pv.parameter_code] = pv.value;
      methodMap[pv.parameter_code] = pv.test_method;
    });

    setEditingSample(sample);
    setEditError(null);
    setEditFormData({
      sample_code: sample.sample_code || '',
      district: sample.location?.district || MADURAI_DISTRICT,
      taluk_block: sample.location?.taluk_block || sample.location?.name || MADURAI_BLOCKS[0],
      village: sample.location?.village || '',
      sample_date: sample.sample_date || new Date().toISOString().split('T')[0],
      depth_cm: sample.depth_cm || 20,
      land_use: sample.land_use || COMMON_CROPS[0],
      collector_name: sample.collector_name || '',
      notes: sample.notes || '',
      data_source: sample.data_source || 'verified',
      // Parameters
      ph: paramMap.ph !== undefined ? paramMap.ph : 7.2,
      ph_method: methodMap.ph || TESTING_METHODS.ph[0],
      nitrogen: paramMap.nitrogen !== undefined ? paramMap.nitrogen : 280,
      nitrogen_method: methodMap.nitrogen || TESTING_METHODS.nitrogen[0],
      phosphorus: paramMap.phosphorus !== undefined ? paramMap.phosphorus : 16,
      phosphorus_method: methodMap.phosphorus || TESTING_METHODS.phosphorus[0],
      potassium: paramMap.potassium !== undefined ? paramMap.potassium : 220,
      potassium_method: methodMap.potassium || TESTING_METHODS.potassium[0],
    });
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Live rating preview calculation for edit form
  const getEstimatedRating = () => {
    if (!editFormData) return null;
    const ph = parseFloat(editFormData.ph);
    const n = parseFloat(editFormData.nitrogen);
    const p = parseFloat(editFormData.phosphorus);
    const k = parseFloat(editFormData.potassium);

    let phClass = 'Neutral';
    if (ph < 4.5) phClass = 'Extremely Acidic';
    else if (ph < 5.5) phClass = 'Strongly Acidic';
    else if (ph < 6.5) phClass = 'Slightly Acidic';
    else if (ph <= 7.3) phClass = 'Neutral (Optimal)';
    else if (ph <= 8.4) phClass = 'Moderately Alkaline';
    else phClass = 'Strongly Alkaline';

    const nClass = n < 240 ? 'Low' : n <= 480 ? 'Medium' : 'High';
    const pClass = p < 11 ? 'Low' : p <= 22 ? 'Medium' : 'High';
    const kClass = k < 110 ? 'Low' : k <= 280 ? 'Medium' : 'High';

    const scores = [
      nClass === 'Low' ? 1 : nClass === 'Medium' ? 2 : 3,
      pClass === 'Low' ? 1 : pClass === 'Medium' ? 2 : 3,
      kClass === 'Low' ? 1 : kClass === 'Medium' ? 2 : 3,
    ];
    const avg = scores.reduce((a, b) => a + b, 0) / 3;
    const rounded = Math.round(avg * 100) / 100;
    const fertilityClass = rounded < 1.67 ? 'Low' : rounded <= 2.33 ? 'Medium' : 'High';

    return { phClass, nClass, pClass, kClass, fertilityClass };
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editingSample || !editFormData) return;
    setEditSaving(true);
    setEditError(null);

    try {
      const locationName = editFormData.village
        ? `${editFormData.village}, ${editFormData.taluk_block}`
        : editFormData.taluk_block;

      const payload = {
        sample_code: editFormData.sample_code.trim(),
        location_name: locationName,
        district: editFormData.district || MADURAI_DISTRICT,
        taluk_block: editFormData.taluk_block,
        village: editFormData.village || editFormData.taluk_block,
        sample_date: editFormData.sample_date,
        depth_cm: parseFloat(editFormData.depth_cm) || 20,
        land_use: editFormData.land_use,
        collector_name: editFormData.collector_name || 'Agricultural Officer',
        notes: editFormData.notes,
        data_source: editFormData.data_source,
        parameters: [
          {
            parameter_code: 'ph',
            value: parseFloat(editFormData.ph),
            unit: 'pH',
            test_method: editFormData.ph_method,
          },
          {
            parameter_code: 'nitrogen',
            value: parseFloat(editFormData.nitrogen),
            unit: 'kg/ha',
            test_method: editFormData.nitrogen_method,
          },
          {
            parameter_code: 'phosphorus',
            value: parseFloat(editFormData.phosphorus),
            unit: 'kg/ha',
            test_method: editFormData.phosphorus_method,
          },
          {
            parameter_code: 'potassium',
            value: parseFloat(editFormData.potassium),
            unit: 'kg/ha',
            test_method: editFormData.potassium_method,
          },
        ],
      };

      await api.updateSample(editingSample.id, payload);
      setSuccessMessage(`Soil sample ${payload.sample_code} updated successfully! Fertility status re-classified.`);
      setEditingSample(null);
      setEditFormData(null);
      fetchSamples(meta.page);
    } catch (err) {
      setEditError(err.message || 'Failed to update soil sample record.');
    } finally {
      setEditSaving(false);
    }
  };

  const editPreview = getEstimatedRating();

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '22px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
            Madurai District Soil Samples Explorer
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Search, filter, edit, and inspect verified laboratory and field soil test records.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={() => fetchSamples(meta.page)} title="Refresh data">
            <RotateCcw size={15} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={() => onNavigate('entry')}>
            <PlusCircle size={16} /> Add Soil Sample
          </button>
        </div>
      </div>

      {/* Success Notification Banner */}
      {successMessage && (
        <div className="alert alert-success" style={{ marginBottom: '18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={18} />
            <span>{successMessage}</span>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => setSuccessMessage(null)} style={{ padding: '4px 8px' }}>
            <X size={14} />
          </button>
        </div>
      )}

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

          {(search || locationId || fertilityClass !== 'all' || dataSource !== 'all') && (
            <button type="button" className="btn btn-secondary" onClick={handleResetFilters}>
              Reset
            </button>
          )}
        </form>
      </div>

      {error && (
        <div className="alert alert-danger" style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertCircle size={20} />
            <div>
              <div style={{ fontWeight: 700 }}>Connection or Query Error</div>
              <div style={{ fontSize: '0.85rem' }}>{error}</div>
            </div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => fetchSamples(meta.page)}>
            <RotateCcw size={14} /> Retry
          </button>
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
                  <td colSpan={11} style={{ textAlign: 'center', padding: '50px' }}>
                    <div className="spinner spinner-primary" style={{ margin: '0 auto 12px' }} />
                    <p style={{ color: '#64748b', fontWeight: 500 }}>Fetching live soil sample records…</p>
                  </td>
                </tr>
              ) : samples.length === 0 ? (
                <tr>
                  <td colSpan={11} style={{ textAlign: 'center', padding: '50px 20px', color: '#64748b' }}>
                    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
                      <AlertCircle size={36} color="#94a3b8" style={{ marginBottom: '10px' }} />
                      <div style={{ fontWeight: 700, fontSize: '1rem', color: '#0f172a', marginBottom: '6px' }}>
                        No Soil Samples Found
                      </div>
                      <p style={{ fontSize: '0.85rem', marginBottom: '16px' }}>
                        No records match the active filters or search criteria in the database.
                      </p>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        <button className="btn btn-secondary btn-sm" onClick={handleResetFilters}>
                          Reset Filters
                        </button>
                        <button className="btn btn-primary btn-sm" onClick={() => onNavigate('entry')}>
                          <PlusCircle size={14} /> Add First Sample
                        </button>
                      </div>
                    </div>
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
                            title="View full details"
                            onClick={() => setSelectedSample(s)}
                          >
                            <Eye size={14} />
                          </button>
                          <button
                            className="btn btn-secondary btn-sm"
                            title="Edit soil sample"
                            style={{ color: '#1e40af', borderColor: '#bfdbfe' }}
                            onClick={() => handleOpenEdit(s)}
                          >
                            <Pencil size={14} />
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

      {/* EDIT SOIL SAMPLE MODAL */}
      {editingSample && editFormData && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 60,
            padding: '20px',
          }}
        >
          <div
            className="card"
            style={{
              width: '100%',
              maxWidth: '780px',
              maxHeight: '92vh',
              overflowY: 'auto',
              padding: '24px',
              backgroundColor: '#ffffff',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '18px',
                borderBottom: '1px solid #e2e8f0',
                paddingBottom: '12px',
              }}
            >
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1e40af', margin: 0 }}>
                  Edit Soil Sample: {editingSample.sample_code}
                </h3>
                <p style={{ color: '#64748b', fontSize: '0.82rem', margin: '3px 0 0' }}>
                  Modify sample metadata, location, and chemical parameters. Fertility classification will automatically update.
                </p>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setEditingSample(null)}
                style={{ padding: '6px' }}
              >
                <X size={18} />
              </button>
            </div>

            {editError && (
              <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
                <AlertCircle size={16} />
                <div>{editError}</div>
              </div>
            )}

            <form onSubmit={handleSaveEdit}>
              {/* Section 1: Identification & Location */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#7c3f1d', marginBottom: '10px', textTransform: 'uppercase' }}>
                  1. Sample Identification & Geography
                </div>
                <div className="grid-3" style={{ gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Sample Code *</label>
                    <input
                      type="text"
                      name="sample_code"
                      className="form-control"
                      required
                      value={editFormData.sample_code}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Block / Taluk *</label>
                    <select
                      name="taluk_block"
                      className="form-select"
                      required
                      value={editFormData.taluk_block}
                      onChange={handleEditChange}
                    >
                      {MADURAI_BLOCKS.map((b) => (
                        <option key={b} value={b}>
                          {b}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Village / Locality</label>
                    <input
                      type="text"
                      name="village"
                      className="form-control"
                      placeholder="e.g. Othakadai"
                      value={editFormData.village}
                      onChange={handleEditChange}
                    />
                  </div>
                </div>

                <div className="grid-3" style={{ gap: '12px', marginTop: '10px' }}>
                  <div className="form-group">
                    <label className="form-label">Sampling Date *</label>
                    <input
                      type="date"
                      name="sample_date"
                      className="form-control"
                      required
                      value={editFormData.sample_date}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Sampling Depth (cm)</label>
                    <input
                      type="number"
                      name="depth_cm"
                      className="form-control"
                      min="1"
                      max="200"
                      value={editFormData.depth_cm}
                      onChange={handleEditChange}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Data Source Tag</label>
                    <select
                      name="data_source"
                      className="form-select"
                      value={editFormData.data_source}
                      onChange={handleEditChange}
                    >
                      <option value="verified">Verified Lab Data</option>
                      <option value="demo">Field Survey Assessment</option>
                    </select>
                  </div>
                </div>

                <div className="grid-2" style={{ gap: '12px', marginTop: '10px' }}>
                  <div className="form-group">
                    <label className="form-label">Land Use / Crop</label>
                    <select
                      name="land_use"
                      className="form-select"
                      value={editFormData.land_use}
                      onChange={handleEditChange}
                    >
                      {COMMON_CROPS.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Field Collector Name</label>
                    <input
                      type="text"
                      name="collector_name"
                      className="form-control"
                      placeholder="e.g. S. Ramanathan"
                      value={editFormData.collector_name}
                      onChange={handleEditChange}
                    />
                  </div>
                </div>
              </div>

              {/* Section 2: Soil Chemical Parameters */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#7c3f1d', marginBottom: '10px', textTransform: 'uppercase' }}>
                  2. Chemical Parameters & Laboratory Results
                </div>
                <div className="grid-2" style={{ gap: '14px' }}>
                  {/* pH */}
                  <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div className="form-group" style={{ marginBottom: '8px' }}>
                      <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Soil pH (Acidity / Alkalinity) *</span>
                        <span style={{ fontWeight: 700, color: '#1e40af' }}>{editPreview?.phClass}</span>
                      </label>
                      <input
                        type="number"
                        name="ph"
                        step="0.01"
                        min="0"
                        max="14"
                        className="form-control"
                        required
                        value={editFormData.ph}
                        onChange={handleEditChange}
                      />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Standard: 1:2.5 soil:water electrometric pH meter
                    </div>
                  </div>

                  {/* Nitrogen */}
                  <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div className="form-group" style={{ marginBottom: '8px' }}>
                      <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Available Nitrogen (N in kg/ha) *</span>
                        <span style={{ fontWeight: 700, color: editPreview?.nClass === 'Low' ? '#dc2626' : editPreview?.nClass === 'High' ? '#15803d' : '#d97706' }}>
                          {editPreview?.nClass}
                        </span>
                      </label>
                      <input
                        type="number"
                        name="nitrogen"
                        step="1"
                        min="0"
                        className="form-control"
                        required
                        value={editFormData.nitrogen}
                        onChange={handleEditChange}
                      />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Method: Alkaline KMnO4 (Subbiah & Asija 1956)
                    </div>
                  </div>

                  {/* Phosphorus */}
                  <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div className="form-group" style={{ marginBottom: '8px' }}>
                      <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Available Phosphorus (P in kg/ha) *</span>
                        <span style={{ fontWeight: 700, color: editPreview?.pClass === 'Low' ? '#dc2626' : editPreview?.pClass === 'High' ? '#15803d' : '#d97706' }}>
                          {editPreview?.pClass}
                        </span>
                      </label>
                      <input
                        type="number"
                        name="phosphorus"
                        step="0.1"
                        min="0"
                        className="form-control"
                        required
                        value={editFormData.phosphorus}
                        onChange={handleEditChange}
                      />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Method: Olsen (NaHCO3 pH 8.5)
                    </div>
                  </div>

                  {/* Potassium */}
                  <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div className="form-group" style={{ marginBottom: '8px' }}>
                      <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Available Potassium (K in kg/ha) *</span>
                        <span style={{ fontWeight: 700, color: editPreview?.kClass === 'Low' ? '#dc2626' : editPreview?.kClass === 'High' ? '#15803d' : '#d97706' }}>
                          {editPreview?.kClass}
                        </span>
                      </label>
                      <input
                        type="number"
                        name="potassium"
                        step="1"
                        min="0"
                        className="form-control"
                        required
                        value={editFormData.potassium}
                        onChange={handleEditChange}
                      />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Method: Neutral Normal Ammonium Acetate
                    </div>
                  </div>
                </div>

                {/* Real-time Fertility Classification Preview */}
                <div
                  style={{
                    marginTop: '12px',
                    padding: '12px 16px',
                    backgroundColor: '#faf3eb',
                    borderRadius: '8px',
                    border: '1px solid #ebdcd0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Sparkles size={18} color="#7c3f1d" />
                    <div>
                      <span style={{ fontSize: '0.82rem', color: '#6e5d52', fontWeight: 600 }}>
                        Estimated Overall Fertility Rating:
                      </span>
                      <span
                        style={{
                          marginLeft: '8px',
                          fontWeight: 800,
                          fontSize: '0.95rem',
                          color: '#7c3f1d',
                        }}
                      >
                        {editPreview?.fertilityClass} Fertility
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#7c3f1d' }}>
                    TNAU Agritech Formula
                  </div>
                </div>
              </div>

              {/* Section 3: Notes */}
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">Agronomic Notes / Recommendations</label>
                <textarea
                  name="notes"
                  className="form-control"
                  rows="2"
                  placeholder="Optional field observations or special treatment requirements"
                  value={editFormData.notes}
                  onChange={handleEditChange}
                />
              </div>

              {/* Modal Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={editSaving}
                  onClick={() => setEditingSample(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={editSaving}
                >
                  {editSaving ? <span className="spinner" /> : <CheckCircle size={16} />}
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
                  <strong>Location / Block:</strong> {selectedSample.location?.name || selectedSample.location?.taluk_block || 'Melur'}
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
                className="btn btn-secondary"
                onClick={() => {
                  const s = selectedSample;
                  setSelectedSample(null);
                  handleOpenEdit(s);
                }}
              >
                <Pencil size={15} /> Edit Sample
              </button>
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
