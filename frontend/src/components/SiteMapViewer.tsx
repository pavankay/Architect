import React, { useState, useRef, useEffect } from 'react';

interface Page {
  name: string;
  path: string;
  description?: string;
  children?: Page[];
  features?: string[];
  technical_requirements?: string[];
  user_interactions?: string[];
  data_requirements?: string[];
  seo_considerations?: string[];
}

interface Node {
  id: string;
  name: string;
  path: string;
  x: number;
  y: number;
  page: Page;
  children: string[];
  parent?: string;
}

interface SiteMapViewerProps {
  siteMap: { pages: Page[] };
}

export default function SiteMapViewer({ siteMap }: SiteMapViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Map<string, Node>>(new Map());
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [viewOffset, setViewOffset] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // Update canvas dimensions
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Convert site map to nodes
  useEffect(() => {
    const nodeMap = new Map<string, Node>();
    let yOffset = 200;

    const processPages = (pages: Page[], parentId?: string, depth = 0) => {
      if (!pages || !Array.isArray(pages)) return;
      pages.forEach((page, index) => {
        const id = page.path;
        const node: Node = {
          id,
          name: page.name,
          path: page.path,
          x: 200 + depth * 250,
          y: yOffset,
          page: page,
          children: page.children?.map(c => c.path) || [],
          parent: parentId
        };
        
        nodeMap.set(id, node);
        yOffset += 120;

        if (page.children) {
          processPages(page.children, id, depth + 1);
        }
      });
    };

    if (siteMap && siteMap.pages) {
      processPages(siteMap.pages);
    }
    setNodes(nodeMap);
  }, [siteMap]);

  // Draw the site map
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Save context state
    ctx.save();
    
    // Apply transformations
    ctx.translate(viewOffset.x, viewOffset.y);
    ctx.scale(zoom, zoom);
    
    // Calculate visible area in world coordinates
    const visibleLeft = -viewOffset.x / zoom;
    const visibleTop = -viewOffset.y / zoom;
    const visibleRight = (canvas.width - viewOffset.x) / zoom;
    const visibleBottom = (canvas.height - viewOffset.y) / zoom;
    
    // Draw grid background
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    const gridSize = 20;
    
    // Draw vertical lines
    const startX = Math.floor(visibleLeft / gridSize) * gridSize;
    const endX = Math.ceil(visibleRight / gridSize) * gridSize;
    for (let x = startX; x <= endX; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, visibleTop);
      ctx.lineTo(x, visibleBottom);
      ctx.stroke();
    }
    
    // Draw horizontal lines
    const startY = Math.floor(visibleTop / gridSize) * gridSize;
    const endY = Math.ceil(visibleBottom / gridSize) * gridSize;
    for (let y = startY; y <= endY; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(visibleLeft, y);
      ctx.lineTo(visibleRight, y);
      ctx.stroke();
    }
    
    // Draw dots at intersections
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    const dotGridSize = gridSize * 5;
    const dotStartX = Math.floor(visibleLeft / dotGridSize) * dotGridSize;
    const dotEndX = Math.ceil(visibleRight / dotGridSize) * dotGridSize;
    const dotStartY = Math.floor(visibleTop / dotGridSize) * dotGridSize;
    const dotEndY = Math.ceil(visibleBottom / dotGridSize) * dotGridSize;
    
    for (let x = dotStartX; x <= dotEndX; x += dotGridSize) {
      for (let y = dotStartY; y <= dotEndY; y += dotGridSize) {
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
    // Set styles for connections
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.setLineDash([]);

    // Draw connections with curves
    nodes.forEach(node => {
      node.children.forEach(childId => {
        const child = nodes.get(childId);
        if (child) {
          ctx.beginPath();
          ctx.moveTo(node.x + 100, node.y);
          
          // Create a curved line
          const controlX = (node.x + 100 + child.x - 100) / 2;
          const controlY1 = node.y;
          const controlY2 = child.y;
          
          ctx.bezierCurveTo(
            controlX, controlY1,
            controlX, controlY2,
            child.x - 100, child.y
          );
          ctx.stroke();
        }
      });
    });

    // Draw nodes (minimal info)
    ctx.font = '14px TG Frekuent Mono, monospace';
    nodes.forEach(node => {
      const boxWidth = 200;
      const boxHeight = 60;
      
      // Draw box shadow
      ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillRect(node.x - boxWidth/2 + 2, node.y - boxHeight/2 + 2, boxWidth, boxHeight);
      
      // Draw box
      ctx.fillStyle = '#000000';
      ctx.fillRect(node.x - boxWidth/2, node.y - boxHeight/2, boxWidth, boxHeight);
      ctx.strokeStyle = '#ffffff';
      ctx.strokeRect(node.x - boxWidth/2, node.y - boxHeight/2, boxWidth, boxHeight);
      
      // Draw text
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.font = '14px TG Frekuent Mono, monospace';
      ctx.fillText(node.name, node.x, node.y - 5);
      
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.font = '11px TG Frekuent Mono, monospace';
      ctx.fillText(node.path, node.x, node.y + 15);
    });
    
    // Restore context state
    ctx.restore();
  }, [nodes, viewOffset, zoom, dimensions]);

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - viewOffset.x) / zoom;
    const y = (e.clientY - rect.top - viewOffset.y) / zoom;

    // Check if clicking on a node
    let clickedNode = false;
    nodes.forEach(node => {
      const boxWidth = 200;
      const boxHeight = 60;
      
      if (
        x >= node.x - boxWidth/2 && x <= node.x + boxWidth/2 &&
        y >= node.y - boxHeight/2 && y <= node.y + boxHeight/2
      ) {
        // Check if it's a click (not drag)
        if (!draggingNode) {
          setSelectedNode(node);
        }
        setDraggingNode(node.id);
        setOffset({ x: x - node.x, y: y - node.y });
        clickedNode = true;
      }
    });

    // If not clicking on a node, start panning
    if (!clickedNode) {
      setIsPanning(true);
      setPanStart({ x: e.clientX - viewOffset.x, y: e.clientY - viewOffset.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    if (draggingNode) {
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left - viewOffset.x) / zoom;
      const y = (e.clientY - rect.top - viewOffset.y) / zoom;

      setNodes(prev => {
        const newNodes = new Map(prev);
        const node = newNodes.get(draggingNode);
        if (node) {
          node.x = x - offset.x;
          node.y = y - offset.y;
        }
        return newNodes;
      });
    } else if (isPanning) {
      setViewOffset({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setDraggingNode(null);
    setIsPanning(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(prev => Math.max(0.1, Math.min(3, prev * delta)));
  };

  return (
    <div ref={containerRef} className="w-full h-full relative bg-black overflow-hidden">
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        className="cursor-pointer"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      />
      
      {/* Detail Modal */}
      {selectedNode && (
        <div 
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8"
          onClick={() => setSelectedNode(null)}
        >
          <div 
            className="bg-black border border-white/20 p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="font-mono text-2xl text-white mb-2">{selectedNode.name}</h2>
                <code className="text-white/60 font-mono text-sm bg-white/10 px-2 py-1 rounded">
                  {selectedNode.path}
                </code>
              </div>
              <button 
                onClick={() => setSelectedNode(null)}
                className="text-white/60 hover:text-white font-mono text-xl"
              >
                ×
              </button>
            </div>
            
            {selectedNode.page.description && (
              <div className="mb-6">
                <h3 className="font-mono text-sm text-white/60 mb-2">Description</h3>
                <p className="font-mono text-sm text-white/80">{selectedNode.page.description}</p>
              </div>
            )}
            
            {selectedNode.page.features && selectedNode.page.features.length > 0 && (
              <div className="mb-6">
                <h3 className="font-mono text-sm text-white/60 mb-2">Features</h3>
                <ul className="space-y-1">
                  {selectedNode.page.features.map((feature, i) => (
                    <li key={i} className="font-mono text-sm text-white/80">• {feature}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {selectedNode.page.technical_requirements && selectedNode.page.technical_requirements.length > 0 && (
              <div className="mb-6">
                <h3 className="font-mono text-sm text-white/60 mb-2">Technical Requirements</h3>
                <ul className="space-y-1">
                  {selectedNode.page.technical_requirements.map((req, i) => (
                    <li key={i} className="font-mono text-sm text-white/80">• {req}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {selectedNode.page.user_interactions && selectedNode.page.user_interactions.length > 0 && (
              <div className="mb-6">
                <h3 className="font-mono text-sm text-white/60 mb-2">User Interactions</h3>
                <ul className="space-y-1">
                  {selectedNode.page.user_interactions.map((interaction, i) => (
                    <li key={i} className="font-mono text-sm text-white/80">• {interaction}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {selectedNode.page.data_requirements && selectedNode.page.data_requirements.length > 0 && (
              <div className="mb-6">
                <h3 className="font-mono text-sm text-white/60 mb-2">Data Requirements</h3>
                <ul className="space-y-1">
                  {selectedNode.page.data_requirements.map((data, i) => (
                    <li key={i} className="font-mono text-sm text-white/80">• {data}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {selectedNode.page.seo_considerations && selectedNode.page.seo_considerations.length > 0 && (
              <div className="mb-6">
                <h3 className="font-mono text-sm text-white/60 mb-2">SEO Considerations</h3>
                <ul className="space-y-1">
                  {selectedNode.page.seo_considerations.map((seo, i) => (
                    <li key={i} className="font-mono text-sm text-white/80">• {seo}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}