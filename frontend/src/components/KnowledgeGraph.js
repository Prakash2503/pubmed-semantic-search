import React, { useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const KnowledgeGraph = ({ graphData }) => {
  const fgRef = useRef();

  // Custom function to draw nodes and labels
  const handleNodeCanvasObject = (node, ctx, globalScale) => {
    const label = node.label;
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;

    // Draw the node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color || 'lightblue';
    ctx.fill();

    // Draw the label
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = 'black';
    ctx.fillText(label, node.x, node.y + 8);
  };

  // Node click: open URL or zoom
  const handleNodeClick = useCallback(
    (node) => {
      if (node.url && (node.url.startsWith('http://') || node.url.startsWith('https://'))) {
        window.open(node.url, '_blank');
      } else {
        if (fgRef.current) {
          fgRef.current.centerAt(node.x, node.y, 1000);
          fgRef.current.zoom(4, 1000);
        }
      }
    },
    [fgRef]
  );

  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return <div className="info-message">No graph data could be generated for this query.</div>;
  }

  // Example legend mapping (adjust groups/colors as per your data)
  const legendItems = [
    { color: 'lightblue', label: 'Default / Drug' },
    { color: 'lightgreen', label: 'Treatment' },
    { color: 'lightcoral', label: 'Disease Risk' },
    { color: 'darkblue', label: 'Disease' },
    { color: 'green', label: 'Receptor / Mechanism' }
  ];

  return (
    <div style={{ position: 'relative' }}>
      {/* Graph */}
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeCanvasObject={handleNodeCanvasObject}
        nodeVal={8}
        nodeAutoColorBy="group"
        linkDirectionalArrowLength={6} // Bigger arrows
        linkDirectionalArrowRelPos={1}
        linkLabel="label"
        linkWidth={1}
        onNodeClick={handleNodeClick}
      />

      {/* Legend */}
      <div
        style={{
          position: 'absolute',
          top: 10,
          right: 10,
          background: 'rgba(255,255,255,0.85)',
          padding: '10px',
          borderRadius: '8px',
          fontSize: '12px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.2)'
        }}
      >
        <strong>Legend</strong>
        {legendItems.map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', marginTop: '4px' }}>
            <div
              style={{
                width: '12px',
                height: '12px',
                background: item.color,
                borderRadius: '50%',
                marginRight: '6px'
              }}
            />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KnowledgeGraph;
