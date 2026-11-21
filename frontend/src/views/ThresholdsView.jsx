import React, { useState } from 'react';
import {
  BookOpen,
  ExternalLink,
  ShieldCheck,
  Award,
  Layers,
  Info,
} from 'lucide-react';

export default function ThresholdsView() {
  const [activeTab, setActiveTab] = useState('TNAU');

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto' }}>
      {/* Title */}
      <div style={{ marginBottom: '22px' }}>
        <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
          Scientific Agricultural Thresholds & Rating System
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
          Documented classification standards applied to Madurai District soil nutrient analysis.
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button
          className={`btn ${activeTab === 'TNAU' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('TNAU')}
        >
          <Award size={16} /> TNAU Agritech Standard (Default for Tamil Nadu)
        </button>
        <button
          className={`btn ${activeTab === 'SHC' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('SHC')}
        >
          <Layers size={16} /> ICAR Soil Health Card (SHC) Standard
        </button>
      </div>

      {/* Overview Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <span>{activeTab === 'TNAU' ? 'Tamil Nadu Agricultural University (TNAU) Rating Chart' : 'ICAR-IISS Soil Health Card Standard'}</span>
          <span className="badge badge-verified">Officially Documented</span>
        </div>

        <p style={{ color: '#475569', fontSize: '0.88rem', lineHeight: 1.5, marginBottom: '16px' }}>
          {activeTab === 'TNAU' ? (
            <>
              Sourced from the <strong>TNAU Agritech Soil Rating Chart</strong> (Department of Soil Science and Agricultural Chemistry, Tamil Nadu Agricultural University, Coimbatore). Validated for agro-climatic zones of Tamil Nadu including the southern semi-arid zone of Madurai District.
            </>
          ) : (
            <>
              Sourced from the <strong>ICAR-IISS Bhopal Soil Health Card scheme</strong> (Department of Agriculture and Farmers Welfare, Ministry of Agriculture, Government of India). Implemented nationwide for farm-level soil testing advisory.
            </>
          )}
        </p>

        {/* Macronutrient Thresholds Table */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#7c3f1d', marginBottom: '10px' }}>
          Available Macronutrient Critical Levels (kg/ha)
        </h4>

        <div className="table-container" style={{ marginBottom: '20px' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Nutrient Parameter</th>
                <th>Standard Testing Method</th>
                <th>Low Status</th>
                <th>Medium Status (Target)</th>
                <th>High Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Available Nitrogen (N)</strong></td>
                <td>Alkaline KMnO4 (Subbiah & Asija 1956)</td>
                <td><span className="badge badge-fertility-low">&lt; {activeTab === 'TNAU' ? '240' : '280'} kg/ha</span></td>
                <td><span className="badge badge-fertility-medium">{activeTab === 'TNAU' ? '240 – 480' : '280 – 560'} kg/ha</span></td>
                <td><span className="badge badge-fertility-high">&gt; {activeTab === 'TNAU' ? '480' : '560'} kg/ha</span></td>
              </tr>
              <tr>
                <td><strong>Available Phosphorus (P)</strong></td>
                <td>Olsen (0.5M NaHCO3 pH 8.5)</td>
                <td><span className="badge badge-fertility-low">&lt; {activeTab === 'TNAU' ? '11' : '10'} kg/ha</span></td>
                <td><span className="badge badge-fertility-medium">{activeTab === 'TNAU' ? '11 – 22' : '10 – 25'} kg/ha</span></td>
                <td><span className="badge badge-fertility-high">&gt; {activeTab === 'TNAU' ? '22' : '25'} kg/ha</span></td>
              </tr>
              <tr>
                <td><strong>Available Potassium (K)</strong></td>
                <td>Neutral Normal Ammonium Acetate</td>
                <td><span className="badge badge-fertility-low">&lt; {activeTab === 'TNAU' ? '110' : '108'} kg/ha</span></td>
                <td><span className="badge badge-fertility-medium">{activeTab === 'TNAU' ? '110 – 280' : '108 – 280'} kg/ha</span></td>
                <td><span className="badge badge-fertility-high">&gt; 280 kg/ha</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Soil Reaction (pH) Classes Table */}
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1e40af', marginBottom: '10px' }}>
          Soil Reaction (pH) 9-Tier Classification (IARI Soil Survey Manual 1970 / ICAR-NBSS&LUP)
        </h4>

        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Classification Tier</th>
                <th>pH Range</th>
                <th>Agronomic Characteristic & Management</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Extremely Acidic</td><td>&lt; 4.5</td><td>Severe aluminum & manganese toxicity; heavy liming mandatory.</td></tr>
              <tr><td>Very Strongly Acidic</td><td>4.5 – 5.0</td><td>Restricted phosphorus availability; apply lime/dolomite.</td></tr>
              <tr><td>Strongly Acidic</td><td>5.0 – 5.5</td><td>Low microbial activity; corrective liming needed.</td></tr>
              <tr><td>Moderately Acidic</td><td>5.5 – 6.0</td><td>Slight restriction for sensitive pulses; maintain organic matter.</td></tr>
              <tr><td>Slightly Acidic</td><td>6.0 – 6.5</td><td>Suitable for most crops; good nutrient uptake.</td></tr>
              <tr style={{ backgroundColor: '#f0fdf4' }}>
                <td><strong>Neutral (Optimal)</strong></td>
                <td><strong>6.5 – 7.3</strong></td>
                <td><strong>Ideal availability of all essential macro and micronutrients.</strong></td>
              </tr>
              <tr><td>Slightly Alkaline</td><td>7.3 – 7.8</td><td>Common in Madurai irrigated belts; phosphorus may form calcium phosphates.</td></tr>
              <tr><td>Moderately Alkaline</td><td>7.8 – 8.4</td><td>Apply farmyard manure and green manure (Daincha) to lower soil pH.</td></tr>
              <tr><td>Strongly Alkaline</td><td>8.4 – 9.0</td><td>Micronutrient (Zn, Fe) fixation; apply agricultural gypsum.</td></tr>
              <tr><td>Very Strongly Alkaline</td><td>&gt; 9.0</td><td>Sodic soil condition; reclamation with gypsum and leaching required.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Nutrient Index Formula Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <span>Nutrient Index (NI) Formula & Evaluation Standard</span>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Rammoorthy & Bajaj (1969)</span>
        </div>

        <p style={{ fontSize: '0.88rem', color: '#475569', marginBottom: '12px' }}>
          Regional nutrient fertility indices are computed according to the formula of Parker (1951) and Rammoorthy & Bajaj (1969):
        </p>

        <div style={{ backgroundColor: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', fontFamily: 'monospace', fontSize: '0.95rem', textAlign: 'center', marginBottom: '16px' }}>
          NI = (1 × N_Low + 2 × N_Medium + 3 × N_High) / N_Total
        </div>

        <div className="grid-3" style={{ fontSize: '0.85rem' }}>
          <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
            <strong style={{ color: '#dc2626' }}>Low Fertility Index:</strong> NI &lt; 1.67
            <p style={{ color: '#64748b', fontSize: '0.78rem', marginTop: '4px' }}>
              More than 67% of field samples test low. Boost base fertilizer doses.
            </p>
          </div>
          <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#eff6ff', border: '1px solid #bfdbfe' }}>
            <strong style={{ color: '#1e40af' }}>Medium Fertility Index:</strong> 1.67 ≤ NI ≤ 2.33
            <p style={{ color: '#64748b', fontSize: '0.78rem', marginTop: '4px' }}>
              Balanced nutrient supply. Maintain standard recommended dose.
            </p>
          </div>
          <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
            <strong style={{ color: '#15803d' }}>High Fertility Index:</strong> NI &gt; 2.33
            <p style={{ color: '#64748b', fontSize: '0.78rem', marginTop: '4px' }}>
              High reserves. Reduce application to prevent luxury consumption.
            </p>
          </div>
        </div>
      </div>

      {/* Official Citations & Links */}
      <div className="card">
        <div className="card-title">Scientific References & Official Sources</div>
        <ul style={{ paddingLeft: '20px', fontSize: '0.85rem', color: '#475569', lineHeight: 1.8 }}>
          <li>
            <strong>TNAU Agritech Portal:</strong>{' '}
            <a href="https://agritech.tnau.ac.in" target="_blank" rel="noreferrer" style={{ color: '#1e40af' }}>
              https://agritech.tnau.ac.in <ExternalLink size={12} style={{ display: 'inline' }} />
            </a>
          </li>
          <li>
            <strong>ICAR Soil Health Card Portal (Govt. of India):</strong>{' '}
            <a href="https://soilhealth.dac.gov.in" target="_blank" rel="noreferrer" style={{ color: '#1e40af' }}>
              https://soilhealth.dac.gov.in <ExternalLink size={12} style={{ display: 'inline' }} />
            </a>
          </li>
          <li>
            <strong>IARI Soil Survey Manual (1970):</strong> Indian Agricultural Research Institute, New Delhi.
          </li>
          <li>
            <strong>Krishi Vigyan Kendra (KVK) Madurai:</strong> Agricultural College & Research Institute, Othakadai, Madurai - 625104.
          </li>
        </ul>
      </div>
    </div>
  );
}
