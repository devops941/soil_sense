import React from 'react';
import { ShieldCheck, MapPin, Award, Database } from 'lucide-react';
import { MADURAI_DISTRICT, MADURAI_STATE } from '../constants/madurai';

export default function Navbar({ activeStandard, dataSourceFilter, onDataSourceChange }) {
  return (
    <header className="top-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <MapPin size={17} color="#7c3f1d" />
          <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#7c3f1d' }}>
            {MADURAI_DISTRICT} District
          </span>
          <span style={{ color: '#6e5d52', fontSize: '0.85rem' }}>({MADURAI_STATE})</span>
        </div>

        <div style={{ height: '18px', width: '1px', backgroundColor: '#ebdcd0' }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Award size={15} color="#2e7d32" />
          <span style={{ fontSize: '0.82rem', color: '#6e5d52' }}>
            Standard: <strong>{activeStandard} Agritech</strong>
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Global Data Source Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.84rem' }}>
          <Database size={15} color="#7c3f1d" />
          <span style={{ color: '#6e5d52', fontWeight: 500 }}>Data Source:</span>
          <select
            className="form-select"
            style={{ width: 'auto', padding: '5px 10px', fontSize: '0.82rem' }}
            value={dataSourceFilter}
            onChange={(e) => onDataSourceChange(e.target.value)}
          >
            <option value="all">All Verified Soil Records</option>
            <option value="verified">Verified Lab Data Only</option>
            <option value="demo">Field Survey Records</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="badge badge-verified">
            <ShieldCheck size={12} /> Strictly Madurai
          </span>
        </div>
      </div>
    </header>
  );
}
