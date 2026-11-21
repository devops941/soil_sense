import React from 'react';
import {
  Home,
  LayoutDashboard,
  TableProperties,
  PlusCircle,
  UploadCloud,
  BarChart3,
  FileText,
  BookOpen,
  Sprout,
  ShieldCheck,
} from 'lucide-react';

export default function Sidebar({ currentTab, onSelectTab, demoCount = 0 }) {
  const menuItems = [
    { id: 'landing', label: 'Home / Overview', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'samples', label: 'Soil Samples', icon: TableProperties },
    { id: 'entry', label: 'Manual Entry', icon: PlusCircle },
    { id: 'upload', label: 'CSV Upload', icon: UploadCloud },
    { id: 'analytics', label: 'Statistical Analytics', icon: BarChart3 },
    { id: 'reports', label: 'Reports & Exports', icon: FileText },
    { id: 'thresholds', label: 'Thresholds Guide', icon: BookOpen },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div
        style={{ padding: '24px 20px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
        onClick={() => onSelectTab('landing')}
        title="Go to Home / Overview"
      >
        <div
          className="animate-float"
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            backgroundColor: '#7c3f1d',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 4px 6px -1px rgba(124, 63, 29, 0.25)',
          }}
        >
          <Sprout size={24} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#7c3f1d', lineHeight: 1.1 }}>
            SoilSense
          </h1>
          <p style={{ fontSize: '0.74rem', color: '#6e5d52', fontWeight: 500 }}>
            Madurai Nutrient Intel
          </p>
        </div>
      </div>

      {/* Nav Menu */}
      <nav style={{ flex: 1, padding: '10px 0' }}>
        <div style={{ padding: '0 20px 8px', fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
          Menu
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {isActive && (
                <span
                  className="pulse-dot"
                  style={{ marginLeft: 'auto', width: '6px', height: '6px', backgroundColor: '#ffffff', boxShadow: 'none' }}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Soil Quality Assurance Notice */}
      <div style={{ padding: '16px', margin: '14px', borderRadius: '10px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', fontSize: '0.78rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#166534', fontWeight: 700, marginBottom: '4px' }}>
          <ShieldCheck size={14} color="#16a34a" /> Data Integrity
        </div>
        <p style={{ color: '#166534', lineHeight: 1.35, margin: 0 }}>
          Madurai District Soil Network. 100% verified records under official TNAU Agritech Standards.
        </p>
      </div>

      {/* Version Footer */}
      <div style={{ padding: '14px 20px', borderTop: '1px solid #ebdcd0', fontSize: '0.75rem', color: '#9e8e82' }}>
        SoilSense v0.1.0 • Tamil Nadu
      </div>
    </aside>
  );
}
