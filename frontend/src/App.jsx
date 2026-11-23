import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import LandingPageView from './views/LandingPageView';
import DashboardView from './views/DashboardView';
import SamplesView from './views/SamplesView';
import ManualEntryView from './views/ManualEntryView';
import UploadView from './views/UploadView';
import AnalyticsView from './views/AnalyticsView';
import ReportsView from './views/ReportsView';
import { api } from './services/api';

export default function App() {
  const [currentTab, setCurrentTab] = useState('landing');
  const [dataSourceFilter, setDataSourceFilter] = useState('all');
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [preFillData, setPreFillData] = useState(null);

  const fetchSummary = async () => {
    try {
      setLoadingSummary(true);
      const data = await api.getDashboardSummary(dataSourceFilter);
      setSummary(data);
    } catch (err) {
      console.error('Failed to load dashboard summary:', err);
    } finally {
      setLoadingSummary(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [dataSourceFilter, currentTab]);

  const handleDownloadSamplePdf = (sampleId, sampleCode) => {
    const url = api.getSamplePdfUrl(sampleId);
    const link = document.createElement('a');
    link.href = url;
    link.download = `soilsense_sample_${sampleCode}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePreFillEntry = (data) => {
    setPreFillData(data);
    setCurrentTab('entry');
  };

  const renderCurrentView = () => {
    switch (currentTab) {
      case 'landing':
        return (
          <LandingPageView
            onNavigate={setCurrentTab}
            onPreFillEntry={handlePreFillEntry}
            summary={summary}
          />
        );
      case 'dashboard':
        return (
          <DashboardView
            summary={summary}
            loading={loadingSummary}
            onNavigate={setCurrentTab}
            onDownloadSamplePdf={handleDownloadSamplePdf}
            onRetry={fetchSummary}
          />
        );
      case 'samples':
        return (
          <SamplesView
            onNavigate={setCurrentTab}
            onDownloadSamplePdf={handleDownloadSamplePdf}
          />
        );
      case 'entry':
        return (
          <ManualEntryView
            onNavigate={setCurrentTab}
            onDownloadSamplePdf={handleDownloadSamplePdf}
            preFillData={preFillData}
          />
        );
      case 'upload':
        return <UploadView onNavigate={setCurrentTab} />;
      case 'analytics':
        return <AnalyticsView />;
      case 'reports':
        return (
          <ReportsView
            summary={summary}
            onDownloadSamplePdf={handleDownloadSamplePdf}
          />
        );
      default:
        return (
          <LandingPageView
            onNavigate={setCurrentTab}
            onPreFillEntry={handlePreFillEntry}
            summary={summary}
          />
        );
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        demoCount={summary?.demo_count || 0}
      />

      {/* Main Content Area */}
      <div className="main-content">
        <Navbar
          activeStandard={summary?.active_standard || 'TNAU'}
          dataSourceFilter={dataSourceFilter}
          onDataSourceChange={setDataSourceFilter}
        />
        <main className="content-body animate-fade-in" key={currentTab}>
          {renderCurrentView()}
        </main>

        {/* Global Footer for All Pages */}
        <footer className="app-footer">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 700, color: '#7c3f1d' }}>Soil sense @2026</span>
              <span style={{ color: '#d7c1b0' }}>•</span>
              <span style={{ color: '#6e5d52', fontSize: '0.82rem' }}>Soil Nutrient Intelligence & Precision Agriculture</span>
            </div>
            <div style={{ color: '#9e8e82', fontSize: '0.8rem' }}>
              Madurai District, Tamil Nadu • Conforming to TNAU & ICAR Standards
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
