import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Calculator,
  Table,
  Activity,
  Layers,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';
import PlotlyChart from '../components/PlotlyChart';
import { api } from '../services/api';

export default function AnalyticsView() {
  const [summaryStats, setSummaryStats] = useState([]);
  const [correlation, setCorrelation] = useState({ labels: [], matrix: [] });
  const [selectedParam, setSelectedParam] = useState('ph');
  const [distributionData, setDistributionData] = useState(null);
  const [locations, setLocations] = useState([]);
  const [tTestReq, setTTestReq] = useState({
    parameter_code: 'ph',
    location_id_a: '',
    location_id_b: '',
  });
  const [tTestRes, setTTestRes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tTestLoading, setTTestLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  useEffect(() => {
    loadParamDistribution(selectedParam);
  }, [selectedParam]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [statsRes, corrRes, locRes] = await Promise.all([
        api.getSummaryStats('all'),
        api.getCorrelationMatrix('all'),
        api.getLocations(),
      ]);
      setSummaryStats(statsRes.data || []);
      setCorrelation(corrRes || { labels: [], matrix: [] });
      setLocations(locRes.data || []);
      if (locRes.data && locRes.data.length >= 2) {
        setTTestReq((prev) => ({
          ...prev,
          location_id_a: locRes.data[0].id,
          location_id_b: locRes.data[1].id,
        }));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadParamDistribution = async (param) => {
    try {
      const res = await api.getDistribution(param, 15, 'all');
      setDistributionData(res);
    } catch {
      // ignore
    }
  };

  const handleRunTTest = async (e) => {
    e.preventDefault();
    if (!tTestReq.location_id_a || !tTestReq.location_id_b) return;
    try {
      setTTestLoading(true);
      const res = await api.runTTest({
        parameter_code: tTestReq.parameter_code,
        location_id_a: parseInt(tTestReq.location_id_a),
        location_id_b: parseInt(tTestReq.location_id_b),
        data_source: 'all',
      });
      setTTestRes(res);
    } catch (err) {
      alert(`t-test error: ${err.message}`);
    } finally {
      setTTestLoading(false);
    }
  };

  // Correlation Matrix Heatmap
  const corrChartData = [
    {
      z: correlation.matrix,
      x: correlation.labels.map((l) => l.toUpperCase()),
      y: correlation.labels.map((l) => l.toUpperCase()),
      type: 'heatmap',
      colorscale: 'YlOrBr',
      zmin: -1,
      zmax: 1,
    },
  ];

  const corrChartLayout = {
    margin: { t: 20, r: 20, b: 40, l: 60 },
  };

  // Histogram Chart
  const histChartData = distributionData
    ? [
        {
          x: distributionData.bins.slice(0, -1),
          y: distributionData.counts,
          type: 'bar',
          marker: { color: '#7c3f1d' },
        },
      ]
    : [];

  const histChartLayout = {
    xaxis: { title: `${selectedParam.toUpperCase()} Value Ranges` },
    yaxis: { title: 'Frequency (Sample Count)' },
    margin: { t: 20, r: 20, b: 45, l: 45 },
  };

  return (
    <div>
      {/* Title */}
      <div style={{ marginBottom: '22px' }}>
        <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
          Statistical Analysis & Nutrient Metrics
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
          Parametric descriptive statistics, distributions, correlation analysis, and hypothesis testing for Madurai District.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger">
          <AlertCircle size={18} />
          <div>{error}</div>
        </div>
      )}

      {/* Summary Statistics Table */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <span>Descriptive Statistics (Pandas / SciPy Engine)</span>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Madurai District Soil Samples</span>
        </div>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Count</th>
                <th>Mean</th>
                <th>Median</th>
                <th>Std Dev (σ)</th>
                <th>Min</th>
                <th>Max</th>
                <th>25th Percentile</th>
                <th>7th Percentile</th>
              </tr>
            </thead>
            <tbody>
              {summaryStats.map((st) => (
                <tr key={st.parameter_code}>
                  <td style={{ fontWeight: 700, textTransform: 'uppercase', color: '#7c3f1d' }}>
                    {st.parameter_code}
                  </td>
                  <td>{st.count}</td>
                  <td>
                    <strong>{st.mean.toFixed(2)}</strong>
                  </td>
                  <td>{st.median.toFixed(2)}</td>
                  <td>{st.std.toFixed(2)}</td>
                  <td>{st.min.toFixed(2)}</td>
                  <td>{st.max.toFixed(2)}</td>
                  <td>{st.p25.toFixed(2)}</td>
                  <td>{st.p75.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 2-Column: Correlation Heatmap + Distribution Histogram */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        {/* Correlation Heatmap */}
        <div className="card">
          <div className="card-title">
            <span>Pearson Correlation Matrix</span>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>r ∈ [-1.0, 1.0]</span>
          </div>
          <PlotlyChart data={corrChartData} layout={corrChartLayout} style={{ height: '320px' }} />
        </div>

        {/* Distribution Histogram */}
        <div className="card">
          <div className="card-title">
            <span>Parameter Histogram Distribution</span>
            <div style={{ width: '130px' }}>
              <select
                className="form-select"
                style={{ padding: '3px 8px', fontSize: '0.8rem' }}
                value={selectedParam}
                onChange={(e) => setSelectedParam(e.target.value)}
              >
                <option value="ph">Soil pH</option>
                <option value="nitrogen">Nitrogen</option>
                <option value="phosphorus">Phosphorus</option>
                <option value="potassium">Potassium</option>
              </select>
            </div>
          </div>
          <PlotlyChart data={histChartData} layout={histChartLayout} style={{ height: '320px' }} />
        </div>
      </div>

      {/* Hypothesis Testing Tool (Welch's t-test) */}
      <div className="card">
        <div className="card-title">
          <span>Welch's Two-Sample t-Test (Location Hypothesis Testing)</span>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Assesses statistically significant differences (p &lt; 0.05)</span>
        </div>

        <form onSubmit={handleRunTTest} style={{ marginBottom: '16px' }}>
          <div className="grid-4" style={{ alignItems: 'flex-end' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Soil Parameter</label>
              <select
                className="form-select"
                value={tTestReq.parameter_code}
                onChange={(e) => setTTestReq({ ...tTestReq, parameter_code: e.target.value })}
              >
                <option value="ph">Soil pH</option>
                <option value="nitrogen">Available Nitrogen (N)</option>
                <option value="phosphorus">Available Phosphorus (P)</option>
                <option value="potassium">Available Potassium (K)</option>
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Location A</label>
              <select
                className="form-select"
                value={tTestReq.location_id_a}
                onChange={(e) => setTTestReq({ ...tTestReq, location_id_a: e.target.value })}
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Location B</label>
              <select
                className="form-select"
                value={tTestReq.location_id_b}
                onChange={(e) => setTTestReq({ ...tTestReq, location_id_b: e.target.value })}
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary" disabled={tTestLoading}>
              {tTestLoading ? <span className="spinner" /> : <Calculator size={16} />}
              Compute Welch t-Test
            </button>
          </div>
        </form>

        {tTestRes && (
          <div style={{ backgroundColor: '#faf5ef', padding: '16px', borderRadius: '10px', border: '1px solid #ebdcd0' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>
                Test Results: {tTestReq.parameter_code.toUpperCase()} Comparison
              </div>
              <span
                className={`badge ${
                  tTestRes.statistic === null
                    ? 'badge-demo'
                    : tTestRes.significant
                    ? 'badge-fertility-high'
                    : 'badge-fertility-medium'
                }`}
              >
                {tTestRes.statistic === null
                  ? 'Sample Size Notice'
                  : tTestRes.significant
                  ? 'Statistically Significant (p < 0.05)'
                  : 'No Significant Difference (p ≥ 0.05)'}
              </span>
            </div>

            <div className="grid-4" style={{ fontSize: '0.88rem', marginBottom: tTestRes.message ? '10px' : '0' }}>
              <div>
                <strong>
                  {locations.find((l) => String(l.id) === String(tTestReq.location_id_a))?.name || 'Location A'} Mean:
                </strong>{' '}
                {tTestRes.mean_a} (n={tTestRes.n_a})
              </div>
              <div>
                <strong>
                  {locations.find((l) => String(l.id) === String(tTestReq.location_id_b))?.name || 'Location B'} Mean:
                </strong>{' '}
                {tTestRes.mean_b} (n={tTestRes.n_b})
              </div>
              <div>
                <strong>t-Statistic:</strong> {tTestRes.statistic !== null && tTestRes.statistic !== undefined ? tTestRes.statistic : 'N/A'}
              </div>
              <div>
                <strong>p-Value:</strong> {tTestRes.p_value !== null && tTestRes.p_value !== undefined ? tTestRes.p_value : 'N/A'}
              </div>
            </div>

            {tTestRes.message && (
              <div style={{ padding: '8px 12px', backgroundColor: '#fef3c7', borderRadius: '6px', fontSize: '0.8rem', color: '#92400e', border: '1px solid #fde68a' }}>
                ℹ️ {tTestRes.message}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
