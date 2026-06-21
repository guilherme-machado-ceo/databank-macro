/* ═══════════════════════════════════════════════════════
   DATA BANK — Charts & Visualization Engine
   Prepared for future D3.js / Chart.js integration.
   Currently renders simple canvas-based placeholders.
   ═══════════════════════════════════════════════════════ */

const DataBankCharts = {
  initialized: false,

  init() {
    if (this.initialized) return;
    this.initialized = true;

    document.querySelectorAll('[data-chart]').forEach(el => {
      const type = el.dataset.chart;
      this.render(type, el);
    });
  },

  render(type, container) {
    switch (type) {
      case 'mini-sparkline':
        this.renderSparkline(container);
        break;
      case 'radar-placeholder':
        this.renderRadarPlaceholder(container);
        break;
      default:
        this.renderPlaceholder(container, type);
    }
  },

  /* Simple sparkline for economy preview */
  renderSparkline(container) {
    const canvas = document.createElement('canvas');
    canvas.width = container.offsetWidth || 200;
    canvas.height = 60;
    canvas.style.width = '100%';
    canvas.style.height = '60px';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    const points = 30;
    const data = [];

    let val = 30 + Math.random() * 20;
    for (let i = 0; i < points; i++) {
      val += (Math.random() - 0.48) * 5;
      val = Math.max(10, Math.min(50, val));
      data.push(val);
    }

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    ctx.beginPath();
    data.forEach((v, i) => {
      const x = (i / (points - 1)) * w;
      const y = h - ((v - min) / range) * (h - 8) - 4;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    ctx.strokeStyle = '#00d4aa';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Glow
    const gradient = ctx.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, 'rgba(0, 212, 170, 0.15)');
    gradient.addColorStop(1, 'rgba(0, 212, 170, 0)');

    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
  },

  /* Radar placeholder for future π-Radical visualization */
  renderRadarPlaceholder(container) {
    const canvas = document.createElement('canvas');
    canvas.width = container.offsetWidth || 280;
    canvas.height = 280;
    canvas.style.width = '100%';
    canvas.style.maxWidth = '280px';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const cx = 140, cy = 140, r = 100;
    const axes = 6;
    const values = [0.8, 0.6, 0.9, 0.7, 0.75, 0.85];
    const labels = ['ρ₁', 'ρ₂', 'ρ₃', 'ρ₄', 'ρ₅', 'ρ₆'];

    // Grid
    for (let ring = 1; ring <= 4; ring++) {
      ctx.beginPath();
      const rr = (ring / 4) * r;
      for (let i = 0; i <= axes; i++) {
        const angle = (i / axes) * Math.PI * 2 - Math.PI / 2;
        const x = cx + Math.cos(angle) * rr;
        const y = cy + Math.sin(angle) * rr;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = 'rgba(30, 30, 46, 0.8)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Axes
    for (let i = 0; i < axes; i++) {
      const angle = (i / axes) * Math.PI * 2 - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(angle) * r, cy + Math.sin(angle) * r);
      ctx.strokeStyle = 'rgba(30, 30, 46, 0.5)';
      ctx.stroke();

      // Labels
      const lx = cx + Math.cos(angle) * (r + 20);
      const ly = cy + Math.sin(angle) * (r + 20);
      ctx.fillStyle = '#7a756f';
      ctx.font = '12px "DM Mono", monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(labels[i], lx, ly);
    }

    // Data polygon
    ctx.beginPath();
    values.forEach((v, i) => {
      const angle = (i / axes) * Math.PI * 2 - Math.PI / 2;
      const x = cx + Math.cos(angle) * r * v;
      const y = cy + Math.sin(angle) * r * v;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 212, 170, 0.12)';
    ctx.fill();
    ctx.strokeStyle = '#00d4aa';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Data points
    values.forEach((v, i) => {
      const angle = (i / axes) * Math.PI * 2 - Math.PI / 2;
      const x = cx + Math.cos(angle) * r * v;
      const y = cy + Math.sin(angle) * r * v;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#00d4aa';
      ctx.fill();
    });
  },

  renderPlaceholder(container, type) {
    const div = document.createElement('div');
    div.className = 'chart-area';
    div.textContent = `[${type}] — Dashboard interativo em breve`;
    container.appendChild(div);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  DataBankCharts.init();
});
