import React, { useEffect, useState } from "react";
import ReactFlow, {
  addEdge,
  ConnectionLineType,
  applyNodeChanges,
  applyEdgeChanges,
  MiniMap,
  Controls,
  Background,
  MarkerType,
} from 'reactflow';
import { useBlockGraph } from "./api_get";
import { getLayoutedElements } from "./Layout_element";
import 'reactflow/dist/style.css';
import '../styles/default_graph.css';

const BlockGraph = ({ block }) => {
  const { data: nodeData, isSuccess } = useBlockGraph();

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  const proOptions = {
    account: 'paid-pro',
    hideAttribution: true,
  };

  const defaultEdgeOptions = {
    type: 'smoothstep',
    markerEnd: { type: MarkerType.ArrowClosed },
    pathOptions: { offset: 5 }
  };

  useEffect(() => {
    const start = () => {
      const newNodes = [];
      const newEdges = [];
      Object.values(nodeData || {}).forEach(pdfData => {
        newNodes.push(...(pdfData[block]?.initialNodes || []));
        newEdges.push(...(pdfData[block]?.initialEdges || []));
      });
      graph(newNodes, newEdges);
    };

    if (isSuccess) start();
  }, [isSuccess, nodeData, block]);

  const graph = (nodes, edges) => {
    if (nodes && edges) {
      // Extract node IDs from edges
      const nodeIdsFromEdges = new Set(edges.flatMap(edge => [edge.source, edge.target]));

      // Filter nodes to include only those present in the edges
      const filteredNodes = nodes.filter(node => nodeIdsFromEdges.has(node.id));

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(filteredNodes, edges, 'LR');

      setNodes([...layoutedNodes]);
      setEdges([...layoutedEdges]);
    }
  };

  const onConnect = (params) => {
    const newEdge = { ...params, type: ConnectionLineType.SmoothStep };
    setEdges(eds => addEdge(newEdge, eds));
  };

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={changes => setNodes(nds => applyNodeChanges(changes, nds))}
      onEdgesChange={changes => setEdges(eds => applyEdgeChanges(changes, eds))}
      onConnect={onConnect}
      fitView
      attributionPosition="bottom-left"
      defaultEdgeOptions={defaultEdgeOptions}
      proOptions={proOptions}
      style={{ background: "white" }}
    >
      <Background />
      <MiniMap zoomable pannable className="minimap" />
      <Controls className="controls" />
    </ReactFlow>
  );
};

export default BlockGraph;
