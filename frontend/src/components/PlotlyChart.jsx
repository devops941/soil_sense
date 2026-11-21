import React, { useEffect, useRef } from 'react';

/**
 * Reusable Plotly chart wrapper ensuring clean mounting, resize responsiveness, and error handling.
 */
export default function PlotlyChart({ data = [], layout = {}, config = {}, style = { width: '100%', height: '340px' } }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    if (!window.Plotly) {
      containerRef.current.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">Loading Plotly visualization engine…</div>';
      return;
    }

    const defaultLayout = {
      autosize: true,
      margin: { t: 30, r: 25, l: 45, b: 40 },
      font: { family: 'Plus Jakarta Sans, sans-serif', size: 11, color: '#334155' },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      hoverlabel: { font: { family: 'Plus Jakarta Sans, sans-serif' } },
      ...layout,
    };

    const defaultConfig = {
      responsive: true,
      displayModeBar: false,
      ...config,
    };

    window.Plotly.newPlot(containerRef.current, data, defaultLayout, defaultConfig);

    const handleResize = () => {
      if (containerRef.current && window.Plotly) {
        window.Plotly.Plots.resize(containerRef.current);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current && window.Plotly) {
        window.Plotly.purge(containerRef.current);
      }
    };
  }, [data, layout, config]);

  return <div ref={containerRef} style={style} />;
}
