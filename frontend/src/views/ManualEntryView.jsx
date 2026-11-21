import React, { useState, useEffect } from 'react';
import {
  PlusCircle,
  CheckCircle,
  AlertCircle,
  FileDown,
  Sparkles,
  MapPin,
  Calendar,
} from 'lucide-react';
import { api } from '../services/api';
import { MADURAI_DISTRICT, MADURAI_BLOCKS, COMMON_CROPS, TESTING_METHODS } from '../constants/madurai';

export default function ManualEntryView({ onNavigate, onDownloadSamplePdf, preFillData }) {
  const [formData, setFormData] = useState({
    sample_code: `MDU-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
    district: MADURAI_DISTRICT,
    taluk_block: MADURAI_BLOCKS[0],
    village: '',
    sample_date: new Date().toISOString().split('T')[0],
    depth_cm: 20,
    land_use: COMMON_CROPS[0],
    collector_name: '',
    notes: '',
    data_source: 'verified',
    // Parameters
    ph: 7.2,
    ph_method: TESTING_METHODS.ph[0],
    nitrogen: 280,
    nitrogen_method: TESTING_METHODS.nitrogen[0],
    phosphorus: 16,
    phosphorus_method: TESTING_METHODS.phosphorus[0],
    potassium: 220,
    potassium_method: TESTING_METHODS.potassium[0],
  });

  useEffect(() => {
    if (preFillData) {
      setFormData((prev) => ({
        ...prev,
        ph: preFillData.ph !== undefined ? preFillData.ph : prev.ph,
        nitrogen: preFillData.nitrogen !== undefined ? preFillData.nitrogen : prev.nitrogen,
        phosphorus: preFillData.phosphorus !== undefined ? preFillData.phosphorus : prev.phosphorus,
        potassium: preFillData.potassium !== undefined ? preFillData.potassium : prev.potassium,
      }));
    }
  }, [preFillData]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [createdSample, setCreatedSample] = useState(null);

  // Live estimated rating calculator based on TNAU standards
  const estimateRating = () => {
    const ph = parseFloat(formData.ph);
    const n = parseFloat(formData.nitrogen);
    const p = parseFloat(formData.phosphorus);
    const k = parseFloat(formData.potassium);

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

  const preview = estimateRating();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const locationName = formData.village ? `${formData.village}, ${formData.taluk_block}` : formData.taluk_block;
      const payload = {
        sample_code: formData.sample_code.trim(),
        location_name: locationName,
        district: formData.district,
        taluk_block: formData.taluk_block,
        village: formData.village || formData.taluk_block,
        sample_date: formData.sample_date,
        depth_cm: parseFloat(formData.depth_cm) || 20,
        land_use: formData.land_use,
        collector_name: formData.collector_name || 'Agricultural Officer',
        notes: formData.notes,
        data_source: formData.data_source,
        parameters: [
          {
            parameter_code: 'ph',
            value: parseFloat(formData.ph),
            unit: 'pH',
            test_method: formData.ph_method,
          },
          {
            parameter_code: 'nitrogen',
            value: parseFloat(formData.nitrogen),
            unit: 'kg/ha',
            test_method: formData.nitrogen_method,
          },
          {
            parameter_code: 'phosphorus',
            value: parseFloat(formData.phosphorus),
            unit: 'kg/ha',
            test_method: formData.phosphorus_method,
          },
          {
            parameter_code: 'potassium',
            value: parseFloat(formData.potassium),
            unit: 'kg/ha',
            test_method: formData.potassium_method,
          },
        ],
      };

      const res = await api.createSample(payload);
      setCreatedSample(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCreatedSample(null);
    setFormData((prev) => ({
      ...prev,
      sample_code: `MDU-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`,
      village: '',
      notes: '',
    }));
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto' }}>
      {/* Title */}
      <div style={{ marginBottom: '22px' }}>
        <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
          Manual Soil Sample Entry
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
          Record individual soil laboratory test results for Madurai District. Live classification is performed under TNAU thresholds.
        </p>
      </div>

      {createdSample ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '50%', backgroundColor: '#dcfce7', color: '#15803d', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <CheckCircle size={32} />
          </div>
          <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f172a' }}>
            Soil Sample Successfully Recorded!
          </h3>
          <p style={{ color: '#6e5d52', fontSize: '0.92rem', margin: '8px auto 20px', maxWidth: '480px' }}>
            Sample <strong>{createdSample.sample_code}</strong> has been classified as{' '}
            <strong style={{ color: '#7c3f1d' }}>{createdSample.classification?.fertility_class} Fertility</strong>.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
            <button
              className="btn btn-primary"
              onClick={() => onDownloadSamplePdf(createdSample.id, createdSample.sample_code)}
            >
              <FileDown size={16} /> Download Soil Health Card PDF
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate('samples')}>
              View in Samples Explorer
            </button>
            <button className="btn btn-secondary" onClick={handleReset}>
              Enter Another Sample
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          {error && (
            <div className="alert alert-danger">
              <AlertCircle size={18} />
              <div>{error}</div>
            </div>
          )}

          <div className="grid-3" style={{ gap: '24px', alignItems: 'start' }}>
            {/* Form Column (Span 2) */}
            <div style={{ gridColumn: 'span 2' }}>
              {/* Geographical Details Card */}
              <div className="card" style={{ marginBottom: '20px' }}>
                <div className="card-title">
                  <span>1. Geographical Information</span>
                  <span className="badge badge-verified">Madurai Strict Scope</span>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">District (Strictly Enforced)</label>
                    <input type="text" className="form-control" value="Madurai" disabled style={{ backgroundColor: '#f1f5f9' }} />
                    <div className="form-helper">System accepts Madurai District only.</div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Taluk / Block *</label>
                    <select
                      className="form-select"
                      name="taluk_block"
                      value={formData.taluk_block}
                      onChange={handleChange}
                      required
                    >
                      {MADURAI_BLOCKS.map((b) => (
                        <option key={b} value={b}>
                          {b} Block
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Village / Farm Location</label>
                    <input
                      type="text"
                      className="form-control"
                      name="village"
                      placeholder="e.g. Karungalakudi, Alagarkovil Road"
                      value={formData.village}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Sample ID / Code *</label>
                    <input
                      type="text"
                      className="form-control"
                      name="sample_code"
                      value={formData.sample_code}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Sample Collection Details */}
              <div className="card" style={{ marginBottom: '20px' }}>
                <div className="card-title">2. Sampling & Crop Context</div>

                <div className="grid-3">
                  <div className="form-group">
                    <label className="form-label">Sampling Date *</label>
                    <input
                      type="date"
                      className="form-control"
                      name="sample_date"
                      value={formData.sample_date}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Depth (cm)</label>
                    <input
                      type="number"
                      step="0.1"
                      className="form-control"
                      name="depth_cm"
                      value={formData.depth_cm}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Collector Name</label>
                    <input
                      type="text"
                      className="form-control"
                      name="collector_name"
                      placeholder="Officer / Farmer"
                      value={formData.collector_name}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Land Use / Crop</label>
                    <select
                      className="form-select"
                      name="land_use"
                      value={formData.land_use}
                      onChange={handleChange}
                    >
                      {COMMON_CROPS.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Data Source Verification</label>
                    <select
                      className="form-select"
                      name="data_source"
                      value={formData.data_source}
                      onChange={handleChange}
                    >
                      <option value="verified">Verified (Official Soil-Testing Laboratory)</option>
                      <option value="demo">Field Survey Assessment Record</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Nutrient Parameters Card */}
              <div className="card" style={{ marginBottom: '20px' }}>
                <div className="card-title">3. Soil Test Measurements</div>

                <div className="grid-2">
                  {/* Soil pH */}
                  <div className="form-group">
                    <label className="form-label">Soil pH (0.0 – 14.0) *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="14"
                      className="form-control"
                      name="ph"
                      value={formData.ph}
                      onChange={handleChange}
                      required
                    />
                    <div className="form-helper">Testing method: 1:2.5 electrometric (pH meter)</div>
                  </div>

                  {/* Nitrogen */}
                  <div className="form-group">
                    <label className="form-label">Available Nitrogen (kg/ha) *</label>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      className="form-control"
                      name="nitrogen"
                      value={formData.nitrogen}
                      onChange={handleChange}
                      required
                    />
                    <div className="form-helper">Alkaline KMnO4 (Subbiah & Asija 1956)</div>
                  </div>
                </div>

                <div className="grid-2">
                  {/* Phosphorus */}
                  <div className="form-group">
                    <label className="form-label">Available Phosphorus (kg/ha) *</label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      className="form-control"
                      name="phosphorus"
                      value={formData.phosphorus}
                      onChange={handleChange}
                      required
                    />
                    <div className="form-helper">Olsen (NaHCO3 pH 8.5)</div>
                  </div>

                  {/* Potassium */}
                  <div className="form-group">
                    <label className="form-label">Available Potassium (kg/ha) *</label>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      className="form-control"
                      name="potassium"
                      value={formData.potassium}
                      onChange={handleChange}
                      required
                    />
                    <div className="form-helper">Neutral Normal Ammonium Acetate</div>
                  </div>
                </div>
              </div>

              {/* Submit Buttons */}
              <div style={{ display: 'flex', gap: '12px' }}>
                <button type="submit" className="btn btn-primary" disabled={loading} style={{ flex: 1, padding: '12px' }}>
                  {loading ? (
                    <>
                      <span className="spinner" /> Saving & Classifying…
                    </>
                  ) : (
                    <>
                      <PlusCircle size={18} /> Save & Compute Soil Fertility
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Sidebar Live Preview Column */}
            <div>
              <div className="card" style={{ position: 'sticky', top: '90px' }}>
                <div className="card-title">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Sparkles size={16} color="#7c3f1d" />
                    <span>Live Classification Preview</span>
                  </div>
                </div>

                <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#faf5ef', borderRadius: '10px', marginBottom: '16px', border: '1px solid #ebdcd0' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#7c3f1d', textTransform: 'uppercase' }}>
                    Overall Soil Fertility
                  </div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#7c3f1d', marginTop: '4px' }}>
                    {preview.fertilityClass} Fertility
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#6e5d52' }}>
                    TNAU / Rammoorthy & Bajaj standard
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #ebdcd0' }}>
                    <span style={{ color: '#6e5d52' }}>Soil Reaction (pH):</span>
                    <strong>{preview.phClass}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #ebdcd0' }}>
                    <span style={{ color: '#6e5d52' }}>Available Nitrogen:</span>
                    <strong style={{ color: preview.nClass === 'Low' ? '#c62828' : preview.nClass === 'High' ? '#2e7d32' : '#7c3f1d' }}>
                      {preview.nClass}
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #ebdcd0' }}>
                    <span style={{ color: '#6e5d52' }}>Available Phosphorus:</span>
                    <strong style={{ color: preview.pClass === 'Low' ? '#c62828' : preview.pClass === 'High' ? '#2e7d32' : '#7c3f1d' }}>
                      {preview.pClass}
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0' }}>
                    <span style={{ color: '#6e5d52' }}>Available Potassium:</span>
                    <strong style={{ color: preview.kClass === 'Low' ? '#c62828' : preview.kClass === 'High' ? '#2e7d32' : '#7c3f1d' }}>
                      {preview.kClass}
                    </strong>
                  </div>
                </div>

                <div style={{ marginTop: '16px', padding: '10px', backgroundColor: '#faf5ef', borderRadius: '6px', fontSize: '0.75rem', color: '#6e5d52', border: '1px solid #ebdcd0' }}>
                  Classification thresholds follow the TNAU Agritech Soil Rating Chart.
                </div>
              </div>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
