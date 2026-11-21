import React, { useState } from 'react';
import {
  Sprout,
  ShieldCheck,
  Award,
  ArrowRight,
  UploadCloud,
  FileText,
  Sliders,
  CheckCircle2,
  TrendingUp,
  MapPin,
  ExternalLink,
  ChevronRight,
  BarChart3,
  Sparkles,
} from 'lucide-react';
import { MADURAI_DISTRICT, MADURAI_STATE, MADURAI_BLOCKS } from '../constants/madurai';

export default function LandingPageView({ onNavigate, onPreFillEntry, summary }) {
  // Live Simulator State
  const [simPh, setSimPh] = useState(7.4);
  const [simN, setSimN] = useState(260);
  const [simP, setSimP] = useState(15);
  const [simK, setSimK] = useState(190);

  // Live calculation of fertility rating
  const calculateSimFertility = () => {
    let phLabel = 'Neutral (Optimal)';
    let phColor = '#2e7d32';
    if (simPh < 4.5) { phLabel = 'Extremely Acidic'; phColor = '#c62828'; }
    else if (simPh < 5.5) { phLabel = 'Strongly Acidic'; phColor = '#ea580c'; }
    else if (simPh < 6.5) { phLabel = 'Slightly Acidic'; phColor = '#b45309'; }
    else if (simPh <= 7.3) { phLabel = 'Neutral (Optimal)'; phColor = '#2e7d32'; }
    else if (simPh <= 8.4) { phLabel = 'Moderately Alkaline'; phColor = '#8c4319'; }
    else { phLabel = 'Strongly Alkaline'; phColor = '#451e08'; }

    const nStatus = simN < 240 ? 'Low' : simN <= 480 ? 'Medium' : 'High';
    const pStatus = simP < 11 ? 'Low' : simP <= 22 ? 'Medium' : 'High';
    const kStatus = simK < 110 ? 'Low' : simK <= 280 ? 'Medium' : 'High';

    const scores = [
      nStatus === 'Low' ? 1 : nStatus === 'Medium' ? 2 : 3,
      pStatus === 'Low' ? 1 : pStatus === 'Medium' ? 2 : 3,
      kStatus === 'Low' ? 1 : kStatus === 'Medium' ? 2 : 3,
    ];
    const avgScore = scores.reduce((a, b) => a + b, 0) / 3;
    const rounded = Math.round(avgScore * 100) / 100;
    const overall = rounded < 1.67 ? 'Low' : rounded <= 2.33 ? 'Medium' : 'High';

    return { phLabel, phColor, nStatus, pStatus, kStatus, overall, avgScore: rounded };
  };

  const simResult = calculateSimFertility();

  const handleLaunchWithSimulatorValues = () => {
    if (onPreFillEntry) {
      onPreFillEntry({ ph: simPh, nitrogen: simN, phosphorus: simP, potassium: simK });
    }
    onNavigate('entry');
  };

  return (
    <div style={{ maxWidth: '1140px', margin: '0 auto' }}>
      {/* ====================================================================
          1. Hero Section
         ==================================================================== */}
      <section className="hero-banner animate-slide-up">
        <div className="hero-glow-1 animate-float" />
        <div className="hero-glow-2 animate-float-reverse" />

        {/* Floating Soil Mote Particles */}
        <div className="soil-particle" style={{ width: '8px', height: '8px', top: '25%', left: '15%', animationDuration: '6s', animationDelay: '0s' }} />
        <div className="soil-particle" style={{ width: '12px', height: '12px', top: '65%', left: '28%', animationDuration: '7s', animationDelay: '1.5s' }} />
        <div className="soil-particle" style={{ width: '6px', height: '6px', top: '40%', right: '22%', animationDuration: '5.5s', animationDelay: '0.8s' }} />
        <div className="soil-particle" style={{ width: '10px', height: '10px', top: '75%', right: '12%', animationDuration: '8s', animationDelay: '2.2s' }} />
        <div className="soil-particle" style={{ width: '7px', height: '7px', top: '20%', right: '45%', animationDuration: '6.5s', animationDelay: '3s' }} />

        <div style={{ maxWidth: '780px', position: 'relative', zIndex: 2 }}>
          {/* Geographical Governance Badge */}
          <div className="feature-pill animate-float">
            <span className="pulse-dot" />
            <span>Strictly Scoped to {MADURAI_DISTRICT} District, {MADURAI_STATE}</span>
          </div>

          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, lineHeight: 1.18, marginBottom: '18px', letterSpacing: '-0.02em' }}>
            Soil Nutrient Intelligence & Precision Fertility Classification
          </h1>

          <p style={{ fontSize: '1.05rem', color: '#f5ebe1', lineHeight: 1.65, marginBottom: '32px' }}>
            An advanced agro-informatics system built to evaluate soil reaction (pH), Available Nitrogen (N),
            Phosphorus (P), and Potassium (K). Automated using verified <strong>TNAU Agritech</strong> thresholds
            and <strong>ICAR Soil Health Card</strong> standards.
          </p>

          {/* Action CTAs */}
          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', marginBottom: '36px' }}>
            <button
              className="btn btn-primary btn-lg shine-hover"
              style={{ padding: '14px 28px', fontSize: '0.96rem' }}
              onClick={() => onNavigate('dashboard')}
            >
              Launch Analytics Dashboard <ArrowRight size={18} />
            </button>
            <button
              className="btn btn-secondary btn-lg shine-hover"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.12)', color: '#ffffff', borderColor: 'rgba(255, 255, 255, 0.25)', backdropFilter: 'blur(8px)' }}
              onClick={() => onNavigate('upload')}
            >
              <UploadCloud size={18} /> Ingest Soil Dataset (CSV)
            </button>
            <button
              className="btn btn-secondary btn-lg shine-hover"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.12)', color: '#ffffff', borderColor: 'rgba(255, 255, 255, 0.25)', backdropFilter: 'blur(8px)' }}
              onClick={() => onNavigate('reports')}
            >
              <FileText size={18} /> Download Health Cards (PDF)
            </button>
          </div>

          {/* Micro KPI Highlights */}
          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', borderTop: '1px solid rgba(255,255,255,0.15)', paddingTop: '22px' }}>
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f59e0b' }}>13 Blocks</div>
              <div style={{ fontSize: '0.78rem', color: '#e8ded6' }}>Covered in Madurai</div>
            </div>
            <div style={{ width: '1px', backgroundColor: 'rgba(255,255,255,0.15)' }} />
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#4ade80' }}>TNAU & ICAR</div>
              <div style={{ fontSize: '0.78rem', color: '#e8ded6' }}>Certified Agronomic Rules</div>
            </div>
            <div style={{ width: '1px', backgroundColor: 'rgba(255,255,255,0.15)' }} />
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fbbf24' }}>100% Verified</div>
              <div style={{ fontSize: '0.78rem', color: '#e8ded6' }}>Geographical Enforcement</div>
            </div>
            <div style={{ width: '1px', backgroundColor: 'rgba(255,255,255,0.15)' }} />
            <div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f97316' }}>ReportLab</div>
              <div style={{ fontSize: '0.78rem', color: '#e8ded6' }}>Automated PDF Generation</div>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          2. Interactive Live Soil Test Simulator Widget
         ==================================================================== */}
      <section style={{ marginBottom: '46px' }}>
        <div className="simulator-card animate-fade-in">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#7c3f1d', fontWeight: 700, fontSize: '0.86rem', textTransform: 'uppercase' }}>
                <Sparkles size={16} /> Interactive Live Agronomic Tool
              </div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>
                Test Madurai Soil Fertility Live
              </h2>
            </div>
            <span className="badge badge-verified">Instant TNAU Calculator</span>
          </div>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '24px' }}>
            Adjust the sliders below to simulate actual soil test values and observe how SoilSense automatically classifies
            soil reaction, macronutrient status, and overall fertility grouping in real time.
          </p>

          <div className="grid-2" style={{ gap: '32px', alignItems: 'center' }}>
            {/* Left: Interactive Sliders */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* pH Slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Soil pH (Acidity / Alkalinity):</span>
                  <strong style={{ color: simResult.phColor, fontFamily: 'monospace', fontSize: '1rem' }}>{simPh.toFixed(2)}</strong>
                </div>
                <input
                  type="range"
                  min="3.5"
                  max="10.5"
                  step="0.05"
                  value={simPh}
                  onChange={(e) => setSimPh(parseFloat(e.target.value))}
                  className="range-slider"
                />
                <div className="nutrient-meter-bg">
                  <div
                    className="nutrient-meter-bar"
                    style={{
                      width: `${Math.min(100, Math.max(0, ((simPh - 3.5) / 7.0) * 100))}%`,
                      backgroundColor: simResult.phColor,
                    }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9e8e82', marginTop: '4px' }}>
                  <span>Acidic (&lt;6.5)</span>
                  <span>Neutral (6.5 – 7.3)</span>
                  <span>Alkaline (&gt;7.3)</span>
                </div>
              </div>

              {/* Nitrogen Slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Available Nitrogen (N):</span>
                  <strong style={{ color: '#7c3f1d', fontFamily: 'monospace', fontSize: '1rem' }}>{simN} kg/ha</strong>
                </div>
                <input
                  type="range"
                  min="100"
                  max="600"
                  step="5"
                  value={simN}
                  onChange={(e) => setSimN(parseInt(e.target.value))}
                  className="range-slider"
                />
                <div className="nutrient-meter-bg">
                  <div
                    className="nutrient-meter-bar"
                    style={{
                      width: `${Math.min(100, Math.max(0, ((simN - 100) / 500) * 100))}%`,
                      backgroundColor: simResult.nStatus === 'Low' ? '#c62828' : simResult.nStatus === 'High' ? '#2e7d32' : '#7c3f1d',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9e8e82', marginTop: '4px' }}>
                  <span>Low (&lt;240)</span>
                  <span>Medium (240 – 480)</span>
                  <span>High (&gt;480)</span>
                </div>
              </div>

              {/* Phosphorus Slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Available Phosphorus (P):</span>
                  <strong style={{ color: '#2e7d32', fontFamily: 'monospace', fontSize: '1rem' }}>{simP.toFixed(1)} kg/ha</strong>
                </div>
                <input
                  type="range"
                  min="2"
                  max="40"
                  step="0.5"
                  value={simP}
                  onChange={(e) => setSimP(parseFloat(e.target.value))}
                  className="range-slider"
                />
                <div className="nutrient-meter-bg">
                  <div
                    className="nutrient-meter-bar"
                    style={{
                      width: `${Math.min(100, Math.max(0, ((simP - 2) / 38) * 100))}%`,
                      backgroundColor: simResult.pStatus === 'Low' ? '#c62828' : simResult.pStatus === 'High' ? '#2e7d32' : '#7c3f1d',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9e8e82', marginTop: '4px' }}>
                  <span>Low (&lt;11)</span>
                  <span>Medium (11 – 22)</span>
                  <span>High (&gt;22)</span>
                </div>
              </div>

              {/* Potassium Slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Available Potassium (K):</span>
                  <strong style={{ color: '#b45309', fontFamily: 'monospace', fontSize: '1rem' }}>{simK} kg/ha</strong>
                </div>
                <input
                  type="range"
                  min="50"
                  max="450"
                  step="5"
                  value={simK}
                  onChange={(e) => setSimK(parseInt(e.target.value))}
                  className="range-slider"
                />
                <div className="nutrient-meter-bg">
                  <div
                    className="nutrient-meter-bar"
                    style={{
                      width: `${Math.min(100, Math.max(0, ((simK - 50) / 400) * 100))}%`,
                      backgroundColor: simResult.kStatus === 'Low' ? '#c62828' : simResult.kStatus === 'High' ? '#2e7d32' : '#7c3f1d',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9e8e82', marginTop: '4px' }}>
                  <span>Low (&lt;110)</span>
                  <span>Medium (110 – 280)</span>
                  <span>High (&gt;280)</span>
                </div>
              </div>
            </div>

            {/* Right: Live Classification Result Box */}
            <div
              className="animate-pulse-glow"
              style={{
                backgroundColor: '#faf5ef',
                padding: '24px',
                borderRadius: '16px',
                border: `2px solid ${simResult.overall === 'High' ? '#2e7d32' : simResult.overall === 'Low' ? '#c62828' : '#7c3f1d'}`,
                transition: 'border-color 0.35s ease',
              }}
            >
              <div style={{ textAlign: 'center', marginBottom: '18px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#6e5d52', textTransform: 'uppercase' }}>
                  Computed Overall Fertility
                </div>
                <div
                  key={simResult.overall}
                  className="animate-pop-in"
                  style={{
                    fontSize: '1.9rem',
                    fontWeight: 800,
                    color: simResult.overall === 'High' ? '#2e7d32' : simResult.overall === 'Low' ? '#c62828' : '#7c3f1d',
                    marginTop: '2px',
                  }}
                >
                  {simResult.overall} Fertility
                </div>
                <div style={{ fontSize: '0.8rem', color: '#6e5d52' }}>
                  Composite Score: {simResult.avgScore.toFixed(2)} / 3.00 (Rammoorthy & Bajaj 1969)
                </div>
              </div>

              {/* Parameter Badges */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginBottom: '18px' }}>
                <div style={{ padding: '10px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #ebdcd0', fontSize: '0.82rem' }}>
                  <div style={{ color: '#6e5d52', fontSize: '0.75rem' }}>Soil Reaction:</div>
                  <strong style={{ color: simResult.phColor }}>{simResult.phLabel}</strong>
                </div>
                <div style={{ padding: '10px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #ebdcd0', fontSize: '0.82rem' }}>
                  <div style={{ color: '#6e5d52', fontSize: '0.75rem' }}>Nitrogen (N):</div>
                  <strong style={{ color: '#7c3f1d' }}>{simResult.nStatus} Status</strong>
                </div>
                <div style={{ padding: '10px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #ebdcd0', fontSize: '0.82rem' }}>
                  <div style={{ color: '#6e5d52', fontSize: '0.75rem' }}>Phosphorus (P):</div>
                  <strong style={{ color: '#2e7d32' }}>{simResult.pStatus} Status</strong>
                </div>
                <div style={{ padding: '10px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #ebdcd0', fontSize: '0.82rem' }}>
                  <div style={{ color: '#6e5d52', fontSize: '0.75rem' }}>Potassium (K):</div>
                  <strong style={{ color: '#b45309' }}>{simResult.kStatus} Status</strong>
                </div>
              </div>

              <button
                className="btn btn-primary shine-hover"
                style={{ width: '100%' }}
                onClick={handleLaunchWithSimulatorValues}
              >
                Record This Sample in Database <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ====================================================================
          3. Core Architectural Pillars (4 Features)
         ==================================================================== */}
      <section style={{ marginBottom: '46px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-main)' }}>
            Engineered Specifically for Madurai Agriculture
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: '620px', margin: '8px auto 0' }}>
            Built around strict scientific benchmarks, regional soil survey reports, and automated quality checks.
          </p>
        </div>

        <div className="grid-4" style={{ gap: '20px' }}>
          {/* Pillar 1 */}
          <div className="feature-card shine-hover hover-lift animate-slide-up stagger-1">
            <div className="feature-icon-wrapper" style={{ backgroundColor: '#faf3eb', color: '#7c3f1d' }}>
              <ShieldCheck size={26} />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
              Strict Madurai Scope
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Geographical integrity checks automatically reject non-Madurai soil datasets. Only verified Madurai blocks and taluks are accepted.
            </p>
          </div>

          {/* Pillar 2 */}
          <div className="feature-card shine-hover hover-lift animate-slide-up stagger-2">
            <div className="feature-icon-wrapper" style={{ backgroundColor: '#e8f5e9', color: '#2e7d32' }}>
              <Award size={26} />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
              TNAU Agritech Engine
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Calibrated with Tamil Nadu Agricultural University Soil Rating Charts for Alkaline KMnO4 (N), Olsen (P), and Ammonium Acetate (K).
            </p>
          </div>

          {/* Pillar 3 */}
          <div className="feature-card shine-hover hover-lift animate-slide-up stagger-3">
            <div className="feature-icon-wrapper" style={{ backgroundColor: '#fef3c7', color: '#b45309' }}>
              <TrendingUp size={26} />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
              Nutrient Index (NI)
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Implements Rammoorthy & Bajaj (1969) mathematical nutrient index modeling to classify village-level and regional fertility status.
            </p>
          </div>

          {/* Pillar 4 */}
          <div className="feature-card shine-hover hover-lift animate-slide-up stagger-4">
            <div className="feature-icon-wrapper" style={{ backgroundColor: '#faf3eb', color: '#8c4319' }}>
              <FileText size={26} />
            </div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px' }}>
              Automated PDF Reports
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Generates official, print-ready Soil Health Cards and regional summary reports using ReportLab with tailored fertilizer advisories.
            </p>
          </div>
        </div>
      </section>

      {/* ====================================================================
          4. Madurai District Blocks & Regional Profile
         ==================================================================== */}
      <section style={{ marginBottom: '46px' }}>
        <div className="card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#7c3f1d', fontWeight: 700, fontSize: '0.82rem', textTransform: 'uppercase' }}>
                <MapPin size={16} /> Regional Coverage
              </div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>
                Supported Madurai District Community Development Blocks
              </h2>
            </div>
            <button className="btn btn-outline-primary btn-sm shine-hover" onClick={() => onNavigate('samples')}>
              Explore Sample Records <ArrowRight size={14} />
            </button>
          </div>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '20px' }}>
            SoilSense actively models all 13 official community development blocks across the northern alluvial, central irrigated, and southern semi-arid red soil zones of Madurai District:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
            {MADURAI_BLOCKS.map((block) => (
              <div
                key={block}
                className="block-card shine-hover hover-lift"
                onClick={() => onNavigate('samples')}
              >
                <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#7c3f1d' }}>{block}</div>
                <div style={{ fontSize: '0.76rem', color: '#6e5d52', marginTop: '2px' }}>
                  Madurai District • Tamil Nadu
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================
          5. Institutional Framework & Authority Citations
         ==================================================================== */}
      <section style={{ marginBottom: '32px' }}>
        <div style={{ textAlign: 'center', marginBottom: '22px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
            Scientific Authorities & Institutional Data Sources
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.86rem' }}>
            All soil records strictly comply with accredited agricultural university standards and official TNAU agritech parameters.
          </p>
        </div>

        <div className="grid-3">
          <div className="card" style={{ padding: '20px' }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#7c3f1d', marginBottom: '6px' }}>
              TNAU Agritech Portal
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45, marginBottom: '10px' }}>
              Tamil Nadu Agricultural University soil rating charts, critical nutrient ranges, and fertilizer scheduling.
            </p>
            <a
              href="https://agritech.tnau.ac.in"
              target="_blank"
              rel="noreferrer"
              style={{ fontSize: '0.82rem', color: '#7c3f1d', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
            >
              agritech.tnau.ac.in <ExternalLink size={12} />
            </a>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#2e7d32', marginBottom: '6px' }}>
              ICAR Soil Health Card
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45, marginBottom: '10px' }}>
              Ministry of Agriculture & Farmers Welfare nationwide guidelines for soil health monitoring.
            </p>
            <a
              href="https://soilhealth.dac.gov.in"
              target="_blank"
              rel="noreferrer"
              style={{ fontSize: '0.82rem', color: '#2e7d32', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
            >
              soilhealth.dac.gov.in <ExternalLink size={12} />
            </a>
          </div>

          <div className="card" style={{ padding: '20px' }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#b45309', marginBottom: '6px' }}>
              KVK Madurai Center
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45, marginBottom: '10px' }}>
              Krishi Vigyan Kendra, Agricultural College & Research Institute (AC&RI), Othakadai, Madurai.
            </p>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              AC&RI Madurai 625104
            </span>
          </div>
        </div>
      </section>

      {/* Footer Banner */}
      <div style={{ textAlign: 'center', padding: '24px 0 12px', borderTop: '1px solid var(--border-color)', color: 'var(--text-light)', fontSize: '0.8rem' }}>
        SoilSense — Soil Nutrient Intelligence System • Dedicated exclusively to Madurai District, Tamil Nadu.
      </div>
    </div>
  );
}
