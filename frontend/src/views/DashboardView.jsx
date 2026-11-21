import React from 'react';
import {
  Layers,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  FileDown,
  ArrowRight,
  MapPin,
  Calendar,
} from 'lucide-react';
import PlotlyChart from '../components/PlotlyChart';
import { api } from '../services/api';

export default function DashboardView({ summary, loading, onNavigate, onDownloadSamplePdf, onRetry }) {
  React.useEffect(() => {
    if (!summary && onRetry) {
      onRetry();
    }
  }, [summary, onRetry]);

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '12px' }}>
        <div className="spinner spinner-primary" style={{ width: '32px', height: '32px' }} />
        <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Loading Madurai soil nutrient analytics…</p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '36px 20px', maxWidth: '520px', margin: '30px auto' }}>
        <div style={{ color: '#b45309', marginBottom: '12px' }}>
          <AlertCircle size={38} style={{ display: 'inline-block' }} />
        </div>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '6px' }}>Connecting to SoilSense Backend...</h3>
        <p style={{ color: '#6e5d52', fontSize: '0.86rem', marginBottom: '18px' }}>
          FastAPI backend server-ஐ connect செய்ய முடியவில்லை. backend (Port 8001) இயங்குகிறதா என பார்க்கவும்.
        </p>
        <button className="btn btn-primary" onClick={onRetry || (() => window.location.reload())}>
          Retry Connection
        </button>
      </div>
    );
  }

  const {
    total_samples,
    verified_count,
    demo_count,
    locations_count,
    high_fertility_count,
    medium_fertility_count,
    low_fertility_count,
    fertility_distribution = {},
    nutrient_distribution = {},
    ph_distribution = {},
    location_wise_stats = [],
    nutrient_indices = [],
    recent_samples = [],
    active_standard,
  } = summary;

  // Chart 1: Fertility Distribution Donut Chart
  const fertilityChartData = [
    {
      values: [
        fertility_distribution.High || 0,
        fertility_distribution.Medium || 0,
        fertility_distribution.Low || 0,
      ],
      labels: ['High Fertility', 'Medium Fertility', 'Low Fertility'],
      type: 'pie',
      hole: 0.55,
      marker: {
        colors: ['#2e7d32', '#7c3f1d', '#c62828'],
      },
      textinfo: 'label+percent',
      textposition: 'inside',
      insidetextorientation: 'horizontal',
    },
  ];

  const fertilityChartLayout = {
    showlegend: true,
    legend: { orientation: 'h', y: -0.15 },
    margin: { t: 10, r: 10, b: 20, l: 10 },
  };

  // Chart 2: Nutrient Breakdown Grouped Bar Chart
  const nutrients = ['nitrogen', 'phosphorus', 'potassium'];
  const nutrientLabels = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'];
  const lowValues = nutrients.map((n) => nutrient_distribution[n]?.low || 0);
  const medValues = nutrients.map((n) => nutrient_distribution[n]?.medium || 0);
  const highValues = nutrients.map((n) => nutrient_distribution[n]?.high || 0);

  const nutrientChartData = [
    {
      x: nutrientLabels,
      y: lowValues,
      name: 'Low Status',
      type: 'bar',
      marker: { color: '#c62828' },
    },
    {
      x: nutrientLabels,
      y: medValues,
      name: 'Medium Status',
      type: 'bar',
      marker: { color: '#7c3f1d' },
    },
    {
      x: nutrientLabels,
      y: highValues,
      name: 'High Status',
      type: 'bar',
      marker: { color: '#2e7d32' },
    },
  ];

  const nutrientChartLayout = {
    barmode: 'group',
    legend: { orientation: 'h', y: -0.2 },
    yaxis: { title: 'Number of Samples' },
    margin: { t: 15, r: 15, b: 40, l: 45 },
  };

  // Chart 3: Location Comparison Bar Chart
  const topLocations = location_wise_stats.slice(0, 10);
  const locNames = topLocations.map((l) => l.location_name);
  const locAvgN = topLocations.map((l) => l.avg_nitrogen || 0);
  const locAvgP = topLocations.map((l) => l.avg_phosphorus || 0);
  const locAvgK = topLocations.map((l) => l.avg_potassium || 0);

  const locationChartData = [
    { x: locNames, y: locAvgN, name: 'Avg N (kg/ha)', type: 'bar', marker: { color: '#7c3f1d' } },
    { x: locNames, y: locAvgP, name: 'Avg P (kg/ha)', type: 'bar', marker: { color: '#2e7d32' } },
    { x: locNames, y: locAvgK, name: 'Avg K (kg/ha)', type: 'bar', marker: { color: '#d97706' } },
  ];

  const locationChartLayout = {
    barmode: 'group',
    legend: { orientation: 'h', y: -0.25 },
    xaxis: { tickangle: -25 },
    yaxis: { title: 'kg/ha' },
    margin: { t: 15, r: 15, b: 70, l: 45 },
  };

  // Chart 4: Soil Reaction (pH) Classes Horizontal Bar Chart
  const phKeys = Object.keys(ph_distribution);
  const phCounts = Object.values(ph_distribution);
  const phCleanLabels = phKeys.map((k) => k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()));

  const phChartData = [
    {
      y: phCleanLabels,
      x: phCounts,
      type: 'bar',
      orientation: 'h',
      marker: {
        color: phKeys.map((k) =>
          k.includes('neutral') ? '#2e7d32' : k.includes('acid') ? '#ea580c' : '#8c4319'
        ),
      },
    },
  ];

  const phChartLayout = {
    margin: { t: 10, r: 20, b: 30, l: 140 },
    xaxis: { title: 'Samples' },
  };

  return (
    <div>
      {/* Top Welcome & KPI Header */}
      <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-main)' }}>
            Madurai District Soil Fertility Overview
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            Soil Nutrient Intelligence & Interpretation under {active_standard} Agritech standard.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('upload')}>
            Upload CSV Data
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('entry')}>
            Add New Sample
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-4" style={{ marginBottom: '24px' }}>
        {/* Total Samples */}
        <div className="card kpi-card shine-hover animate-slide-up stagger-1">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>TOTAL SOIL SAMPLES</span>
            <div className="kpi-icon-wrapper" style={{ padding: '6px', backgroundColor: '#faf3eb', borderRadius: '8px', color: '#7c3f1d' }}>
              <Layers size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: 'var(--text-main)' }}>{total_samples}</div>
          <div style={{ display: 'flex', gap: '12px', fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
            <span style={{ color: '#2e7d32', fontWeight: 600 }}>{verified_count} Verified Lab</span>
            <span>•</span>
            <span style={{ color: '#7c3f1d', fontWeight: 600 }}>{demo_count} Field Samples</span>
          </div>
        </div>

        {/* High Fertility */}
        <div className="card kpi-card shine-hover animate-slide-up stagger-2" style={{ borderLeft: '4px solid #2e7d32' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#2e7d32' }}>HIGH FERTILITY</span>
            <div className="kpi-icon-wrapper" style={{ padding: '6px', backgroundColor: '#e8f5e9', borderRadius: '8px', color: '#2e7d32' }}>
              <CheckCircle2 size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#2e7d32' }}>{high_fertility_count}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
            {total_samples ? `${Math.round((high_fertility_count / total_samples) * 100)}% of total samples` : '0%'}
          </div>
          <div className="nutrient-meter-bg">
            <div
              className="nutrient-meter-bar"
              style={{
                width: `${total_samples ? (high_fertility_count / total_samples) * 100 : 0}%`,
                backgroundColor: '#2e7d32',
              }}
            />
          </div>
        </div>

        {/* Medium Fertility */}
        <div className="card kpi-card shine-hover animate-slide-up stagger-3" style={{ borderLeft: '4px solid #7c3f1d' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#7c3f1d' }}>MEDIUM FERTILITY</span>
            <div className="kpi-icon-wrapper" style={{ padding: '6px', backgroundColor: '#faf3eb', borderRadius: '8px', color: '#7c3f1d' }}>
              <TrendingUp size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#7c3f1d' }}>{medium_fertility_count}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
            {total_samples ? `${Math.round((medium_fertility_count / total_samples) * 100)}% of total samples` : '0%'}
          </div>
          <div className="nutrient-meter-bg">
            <div
              className="nutrient-meter-bar"
              style={{
                width: `${total_samples ? (medium_fertility_count / total_samples) * 100 : 0}%`,
                backgroundColor: '#7c3f1d',
              }}
            />
          </div>
        </div>

        {/* Low Fertility */}
        <div className="card kpi-card shine-hover animate-slide-up stagger-4" style={{ borderLeft: '4px solid #c62828' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#c62828' }}>LOW FERTILITY</span>
            <div className="kpi-icon-wrapper" style={{ padding: '6px', backgroundColor: '#fee2e2', borderRadius: '8px', color: '#c62828' }}>
              <AlertCircle size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#c62828' }}>{low_fertility_count}</div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
            {total_samples ? `${Math.round((low_fertility_count / total_samples) * 100)}% of total samples` : '0%'}
          </div>
          <div className="nutrient-meter-bg">
            <div
              className="nutrient-meter-bar"
              style={{
                width: `${total_samples ? (low_fertility_count / total_samples) * 100 : 0}%`,
                backgroundColor: '#c62828',
              }}
            />
          </div>
        </div>
      </div>

      {/* Row 1 Charts: Fertility Donut & Nutrient Status */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <div className="card shine-hover hover-lift">
          <div className="card-title">
            <span>Overall Fertility Grouping</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 500, color: '#64748b' }}>Rammoorthy & Bajaj Standard</span>
          </div>
          <PlotlyChart data={fertilityChartData} layout={fertilityChartLayout} style={{ height: '300px' }} />
        </div>

        <div className="card shine-hover hover-lift">
          <div className="card-title">
            <span>Available Macronutrients Status</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 500, color: '#64748b' }}>N / P / K (TNAU Ratings)</span>
          </div>
          <PlotlyChart data={nutrientChartData} layout={nutrientChartLayout} style={{ height: '300px' }} />
        </div>
      </div>

      {/* Row 2 Charts: Regional Location Comparison & Soil Reaction pH */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <div className="card shine-hover hover-lift">
          <div className="card-title">
            <span>Madurai Block Nutrient Comparison</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 500, color: '#64748b' }}>Averages by Block (kg/ha)</span>
          </div>
          <PlotlyChart data={locationChartData} layout={locationChartLayout} style={{ height: '320px' }} />
        </div>

        <div className="card shine-hover hover-lift">
          <div className="card-title">
            <span>Soil Reaction (pH) Classes</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 500, color: '#64748b' }}>IARI 9-Class System</span>
          </div>
          <PlotlyChart data={phChartData} layout={phChartLayout} style={{ height: '320px' }} />
        </div>
      </div>

      {/* Nutrient Index Benchmarks Box */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <span>District Nutrient Indices (NI)</span>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
            Benchmark: &lt;1.67 Low | 1.67–2.33 Medium | &gt;2.33 High
          </span>
        </div>
        <div className="grid-3">
          {nutrient_indices.map((ni) => {
            const val = ni.index_value;
            const cls = ni.class_label;
            const badgeClass = cls === 'High' ? 'badge-fertility-high' : cls === 'Low' ? 'badge-fertility-low' : 'badge-fertility-medium';
            return (
              <div key={ni.parameter_code} style={{ padding: '16px', borderRadius: '10px', backgroundColor: '#faf5ef', border: '1px solid #ebdcd0' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', textTransform: 'capitalize' }}>
                  Available {ni.parameter_code}
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', margin: '8px 0' }}>
                  <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#7c3f1d' }}>{val.toFixed(3)}</span>
                  <span className={`badge ${badgeClass}`}>{cls} Index</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {cls === 'Low' ? 'Regional replenishment recommended' : cls === 'Medium' ? 'Optimal maintenance dose' : 'Reduce application'}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Samples Table */}
      <div className="card">
        <div className="card-title">
          <span>Recent Soil Samples (Madurai District)</span>
          <button className="btn btn-outline-primary btn-sm" onClick={() => onNavigate('samples')}>
            View All Samples <ArrowRight size={14} />
          </button>
        </div>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Sample ID</th>
                <th>Block / Location</th>
                <th>Date</th>
                <th>pH</th>
                <th>N (kg/ha)</th>
                <th>P (kg/ha)</th>
                <th>K (kg/ha)</th>
                <th>Overall Fertility</th>
                <th>Data Source</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recent_samples.length === 0 ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>
                    No soil samples found.
                  </td>
                </tr>
              ) : (
                recent_samples.map((s) => {
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
                      <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{s.sample_code}</td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{s.location?.name || 'Melur'}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{s.location?.district || 'Madurai'}</div>
                      </td>
                      <td>{s.sample_date}</td>
                      <td>{paramMap.ph !== undefined ? paramMap.ph.toFixed(2) : '-'}</td>
                      <td>{paramMap.nitrogen !== undefined ? paramMap.nitrogen.toFixed(0) : '-'}</td>
                      <td>{paramMap.phosphorus !== undefined ? paramMap.phosphorus.toFixed(1) : '-'}</td>
                      <td>{paramMap.potassium !== undefined ? paramMap.potassium.toFixed(0) : '-'}</td>
                      <td>
                        <span className={`badge ${badgeClass}`}>{fertClass}</span>
                      </td>
                      <td>
                        <span className={`badge ${isVerified ? 'badge-verified' : 'badge-demo'}`}>
                          {isVerified ? 'Verified Lab' : 'Field Survey'}
                        </span>
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary btn-sm"
                          title="Download Soil Health Card PDF"
                          onClick={() => onDownloadSamplePdf(s.id, s.sample_code)}
                        >
                          <FileDown size={14} /> PDF
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
