import React, { useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const KnowledgeGraph = ({ graphData }) => {
  const fgRef = useRef();

  // Custom function to draw nodes and their labels on the canvas
  const handleNodeCanvasObject = (node, ctx, globalScale) => {
    const label = node.label;
    const fontSize = 12 / globalScale; // Font size adjusts with zoom
    ctx.font = `${fontSize}px Sans-Serif`;

    // Draw the node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color || 'lightblue'; // Use color from graph data or a default
    ctx.fill();

    // Draw the node label
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'black';
    ctx.fillText(label, node.x, node.y + 10); // Position label below the node
  };

  // --- UPDATED CLICK HANDLER WITH CORRECT 2D METHODS ---
  const handleNodeClick = useCallback(node => {
    // Check if the node has a valid URL property
    if (node.url && (node.url.startsWith('http://') || node.url.startsWith('https://'))) {
      // Open the URL in a new browser tab
      window.open(node.url, '_blank');
    } else {
      // If no valid URL, zoom in on the node using 2D canvas methods
      if (fgRef.current) {
        // Pan to the node's position
        fgRef.current.centerAt(node.x, node.y, 1000); // 1000ms transition
        // Zoom in to a fixed level (e.g., scale of 4)
        fgRef.current.zoom(4, 1000); // 1000ms transition
      }
    }
  }, [fgRef]);

  // Render a message if there's no graph data
  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return <div className="info-message">No graph data could be generated for this query.</div>;
  }

  // Render the graph component
  return (
    <div className="graph-container">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        
        // --- Component Properties ---
        nodeCanvasObject={handleNodeCanvasObject}
        nodeVal={8}
        nodeAutoColorBy="group"
        
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkLabel="label"
        linkWidth={1}
        
        // Assign our updated click handler
        onNodeClick={handleNodeClick}
      />
    </div>
  );
};

export default KnowledgeGraph;
