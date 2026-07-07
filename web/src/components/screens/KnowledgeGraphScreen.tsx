import { useEffect, useRef } from 'react'
import { Network, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react'
import { useAetheris } from '../../context/AetherisContext'

interface Node {
  id: string;
  label: string;
  type: 'project' | 'skill' | 'rfc' | 'spec' | 'integration';
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface Edge {
  source: string;
  target: string;
}

export default function KnowledgeGraphScreen() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { skills, rfcSpecs, integrations } = useAetheris();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Build standard nodes/edges dynamically
    const nodes: Node[] = [
      { id: 'core', label: 'Aetheris Core', type: 'project', x: 250, y: 150, vx: 0, vy: 0 }
    ];
    const edges: Edge[] = [];

    // Add Skills
    skills?.forEach((s, idx) => {
      const id = `s_${idx}`;
      nodes.push({ id, label: s.name, type: 'skill', x: Math.random() * 500, y: Math.random() * 300, vx: 0, vy: 0 });
      edges.push({ source: 'core', target: id });
    });

    // Add RFCs and Specs
    rfcSpecs?.forEach((r, idx) => {
      const id = `r_${idx}`;
      nodes.push({ id, label: r.id, type: r.type === 'RFC' ? 'rfc' : 'spec', x: Math.random() * 500, y: Math.random() * 300, vx: 0, vy: 0 });
      edges.push({ source: 'core', target: id });
    });

    // Add Integrations
    integrations?.forEach((i, idx) => {
      const id = `i_${idx}`;
      nodes.push({ id, label: i.name, type: 'integration', x: Math.random() * 500, y: Math.random() * 300, vx: 0, vy: 0 });
      edges.push({ source: 'core', target: id });
    });

    let animationId: number;

    function animate() {
      if (!ctx || !canvas) return;
      // Force directed simulation calculation
      for (let i = 0; i < nodes.length; i++) {
        const n1 = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const n2 = nodes[j];
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const dist = Math.sqrt(dx*dx + dy*dy) || 1;
          const force = (100 - dist) * 0.01; // basic repulsion force
          
          n1.vx -= force * (dx/dist);
          n1.vy -= force * (dy/dist);
          n2.vx += force * (dx/dist);
          n2.vy += force * (dy/dist);
        }
      }

      edges.forEach(edge => {
        const n1 = nodes.find(n => n.id === edge.source);
        const n2 = nodes.find(n => n.id === edge.target);
        if (n1 && n2) {
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const dist = Math.sqrt(dx*dx + dy*dy) || 1;
          const force = (dist - 120) * 0.02; // basic attraction force
          
          n1.vx += force * (dx/dist);
          n1.vy += force * (dy/dist);
          n2.vx -= force * (dx/dist);
          n2.vy -= force * (dy/dist);
        }
      });

      // Update positions
      nodes.forEach(n => {
        n.x += n.vx;
        n.y += n.vy;
        // Friction
        n.vx *= 0.85;
        n.vy *= 0.85;

        // Keep inside bounds
        n.x = Math.max(50, Math.min(n.x, 750));
        n.y = Math.max(50, Math.min(n.y, 450));
      });

      // Draw
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw Edges
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.lineWidth = 1.5;
      edges.forEach(edge => {
        const n1 = nodes.find(n => n.id === edge.source);
        const n2 = nodes.find(n => n.id === edge.target);
        if (n1 && n2) {
          ctx.beginPath();
          ctx.moveTo(n1.x, n1.y);
          ctx.lineTo(n2.x, n2.y);
          ctx.stroke();
        }
      });

      // Draw Nodes
      nodes.forEach(n => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, 8, 0, 2*Math.PI);
        if (n.type === 'project') ctx.fillStyle = '#6366f1';
        else if (n.type === 'skill') ctx.fillStyle = '#10b981';
        else if (n.type === 'rfc') ctx.fillStyle = '#f59e0b';
        else if (n.type === 'spec') ctx.fillStyle = '#ef4444';
        else ctx.fillStyle = '#06b6d4';
        
        ctx.fill();

        // Node labels
        ctx.font = '10px Inter';
        ctx.fillStyle = '#8892a8';
        ctx.fillText(n.label, n.x + 12, n.y + 4);
      });

      animationId = requestAnimationFrame(animate);
    }

    animate();

    return () => cancelAnimationFrame(animationId);
  }, [skills, rfcSpecs, integrations]);

  return (
    <div className="animate-in">
      <div className="screen-header">
        <h1 className="screen-title">Interactive Knowledge Graph</h1>
        <p className="screen-subtitle">Dynamic topology linking project modules, capabilities, skills, and validation metrics</p>
      </div>

      <div className="section-card" style={{ padding: 0, position: 'relative' }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={500}
          style={{ width: '100%', height: '500px', display: 'block', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)' }}
        />

        {/* Legend Overlay */}
        <div style={{ position: 'absolute', bottom: '16px', left: '16px', display: 'flex', gap: '12px', background: 'var(--bg-elevated)', padding: '8px 16px', borderRadius: 'var(--radius-md)', border: 'var(--border-subtle)', fontSize: '11px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#6366f1' }} /> Project
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} /> Skill
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} /> RFC
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444' }} /> SPEC
          </div>
        </div>
      </div>
    </div>
  );
}
