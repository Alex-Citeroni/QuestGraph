import React, { useEffect, useState, useMemo, useImperativeHandle, forwardRef } from "react";
import ReactFlow, {
    addEdge,
    ConnectionLineType,
    Controls,
    Background,
    Position,
    Handle,
    MiniMap,
    MarkerType,
    useReactFlow,
    useEdgesState,
    useNodesState
} from 'reactflow';
import { usePdfData } from "./api_get";
import Dagre from "@dagrejs/dagre";
import { getLayoutedElementsPDF } from "./Layout_element";
import 'reactflow/dist/style.css';
import '../styles/default_graph.css';

// PDFStructure component: Renders a ReactFlow graph based on the PDF structure data.
// Props:
// - postDataPdf: Data of the selected PDF.
// - onNodeClick: Function to handle node click events.
// - setOptions: Function to update options state.
// - updateNodes: Function to update nodes state.
// - nodeIdColorMap: Object mapping node IDs to their colors.
// - collapse: Set of node IDs to collapse.
// ref: React reference to expose component's methods to parent components.
const PDFStructure = forwardRef(({ postDataPdf, onNodeClick, setOptions, updateNodes, nodeIdColorMap, collapse }, ref) => {
    const { nod, urls } = usePdfData({ setOptions, updateNodes });
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [url, setUrl] = useState({});
    const [allNodes, setAllNodes] = useState([]);
    const { fitView } = useReactFlow();

    const proOptions = { account: 'paid-pro', hideAttribution: true };

    // useImperativeHandle: Expose component's methods to parent components.
    useImperativeHandle(ref, () => ({
        // resetView: Adjusts the view to fit all elements within the container.
        resetView() {
            setTimeout(() => {
                fitView({ duration: 500, padding: 0.1 });
            }, 50);
        }
    }));

    // filterCollapsedChildren: Recursively filters out the children of collapsed nodes.
    // Input: dagre (Dagre graph instance), node (current node).
    const filterCollapsedChildren = (dagre, node) => {
        const children = dagre.successors(node.id) || [];

        node.data.expandable = !!children.length;

        if (!node.data.expanded) {
            for (const child of children) {
                filterCollapsedChildren(dagre, { id: child, data: {} });
                dagre.removeNode(child);
            }
        }
    };

    // ExpandCollapse: Expands or collapses nodes based on their 'expanded' state.
    // Input: newNodes (Array of nodes), newEdges (Array of edges).
    // Output: Array of expanded nodes.
    const ExpandCollapse = (newNodes, newEdges) => {
        const dagre = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({})).setGraph({ rankdir: "LR" });
        newNodes.forEach((node) => {
            dagre.setNode(node.id, { width: 220, height: 100, data: node.data });
        });
        newEdges.forEach((edge) => {
            dagre.setEdge(edge.source, edge.target);
        });
        newNodes.forEach((node) => {
            filterCollapsedChildren(dagre, node);
        });
        Dagre.layout(dagre);
        const expandedNodes = newNodes.flatMap((node) => {
            if (!dagre.hasNode(node.id)) return [];

            const { x, y } = dagre.node(node.id);

            const position = { x, y };
            const data = { ...node.data };

            return [{ ...node, position, data }];
        });
        return expandedNodes;
    };

    // nodeTypes: Memoized object of custom node types.
    const nodeTypes = useMemo(() => {
        const types = {};

        for (const pdfTitleKey in nod.data || {}) {
            const imagesData = nod.data[pdfTitleKey]?.Images;

            if (imagesData) {
                const nodeTypesData = imagesData.nodeTypes;

                if (nodeTypesData) {
                    for (const key in nodeTypesData) {
                        const nodeType = nodeTypesData[key];
                        setUrl([Object.keys(nodeType)[0]] = Object.values(nodeType)[0]);
                        const CustomComponent = () => (
                            <>
                                <Handle type='target' position={Position.Left} />
                                <img src={Object.values(nodeType)[0]} alt="Node Type" style={{ width: '8vw', height: '100%' }} />
                            </>
                        );
                        types[Object.keys(nodeType)[0]] = CustomComponent;
                    }
                }
            }
        }
        return types;
    }, [nod.data]);

    // getNodesAndEdgesConnectedToSource: Returns all nodes and edges connected to the given node.
    // Input: nodeId (String) - the ID of the node.
    // Output: { nodes: Array, edges: Array }.
    const getNodesAndEdgesConnectedToSource = (nodeId, resultNodes = [], resultEdges = []) => {
        const incomingEdges = edges.filter(edge => edge.target === nodeId);

        incomingEdges.forEach(edge => {
            const connectedNodeId = edge.source;
            const connectedNode = nodes.find(n => n.id === connectedNodeId);

            if (connectedNode) {
                resultNodes.push(connectedNode);
                resultEdges.push(edge);
                const { nodes: subNodes, edges: subEdges } = getNodesAndEdgesConnectedToSource(connectedNodeId);
                resultNodes.push(...subNodes);
                resultEdges.push(...subEdges);
            }
        });

        return { nodes: resultNodes, edges: resultEdges };
    };

    // graph: Sets up the graph with nodes and edges and fits the view.
    // Input: nodes (Array), edges (Array).
    const graph = (nodes, edges) => {
        const ordine = getLayoutedElementsPDF(nodes, edges);
        setNodes(ordine);
        setEdges(edges);
        setTimeout(() => { fitView({ duration: 400, nodes: [nodes] }); }, 0);
    };

    // start: Initializes the graph with data from the API.
    const start = () => {
        const newNodes = [];
        const newEdges = [];
        var ok = false

        for (const pdfTitleKey in nod.data || {}) {
            setOptions((prevOptions) => {
                // Copia l'array esistente
                const newOptions = [...prevOptions];

                for (const title in urls.data) {
                    const url = urls.data[title];
                    // Verifica se la chiave è già presente nelle opzioni esistenti
                    const existingOption = newOptions.find(option => option.pdfTitleKey === title);
                    // Se non è presente, aggiungi una nuova opzione
                    if (!existingOption) newOptions.push({ pdfTitleKey: title, url });
                    // Se è presente, unisci i dati
                    else existingOption.url = url;
                }

                if (newOptions.length > 0) ok = true;

                // Ritorna le nuove opzioni
                return newOptions;
            });

            newNodes.push(...(nod.data[pdfTitleKey]?.initialNodes || []));
            newEdges.push(...(nod.data[pdfTitleKey]?.initialEdges || []));

            updateNodes(newNodes);

            const imagesData = nod.data[pdfTitleKey]?.Images;
            if (imagesData) {
                newNodes.push(...(imagesData.imgNodes || []));
                newEdges.push(...(imagesData.imgEdges || []));
            }
        }
        
        if (ok) {
            const expandedNodes = ExpandCollapse(newNodes, newEdges);
            setAllNodes(newNodes);
            graph(expandedNodes, newEdges);
        }
    }

    useEffect(() => {
        if (nod.isSuccess) start();

        if (postDataPdf && postDataPdf !== 'ALL PDF') {
            const newNodes = [], newEdges = [];
            newNodes.push(...(nod.data[postDataPdf.pdfTitleKey]?.initialNodes || []));
            newEdges.push(...(nod.data[postDataPdf.pdfTitleKey]?.initialEdges || []));
            graph(newNodes, newEdges);
        }

        if (collapse.size > 0) expandNode(collapse);
    }, [nod.isSuccess, nod.data, postDataPdf, setOptions, nodeIdColorMap, fitView]);

    // defaultEdgeOptions: Default options for edges in the graph.
    const defaultEdgeOptions = {
        type: 'smoothstep',
        markerEnd: { type: MarkerType.ArrowClosed },
        pathOptions: { offset: 5 },
    };

    // expandNode: Expands the given nodes and updates the graph.
    // Input: nodeIds (Set of node IDs).
    const expandNode = (nodeIds) => {
        let updatedNodes = [...allNodes];
        let nodesToExpand = new Set(nodeIds); // Creare un Set per un accesso efficiente

        updatedNodes = updatedNodes.map(node => {
            if (nodesToExpand.has(node.id)) {
                return {
                    ...node,
                    data: { ...node.data, expanded: true }
                };
            }
            return node;
        });

        let updatedNodes1 = [...updatedNodes];

        if (nodeIdColorMap && Object.keys(nodeIdColorMap).length > 0) {

            let updatedEdges = [...edges];

            updatedNodes.forEach((node) => {
                const color = nodeIdColorMap[node.id];

                if (color) {
                    const { nodes: connectedNodes, edges: connectedEdges } = getNodesAndEdgesConnectedToSource(node.id);

                    // Update the style here
                    updatedNodes1 = updatedNodes1.map((n) => {
                        if (n.id === node.id || connectedNodes.some(connectedNode => connectedNode.id === n.id)) {
                            return {
                                ...n,
                                style: {
                                    ...n.style,
                                    border: `1px solid black`,
                                    backgroundColor: "rgb(135, 206, 250)",
                                    color: color.color,
                                },
                            };
                        }
                        return n;
                    });

                    // Aggiorna lo stile degli edge collegati
                    updatedEdges = updatedEdges.map((edge) => {
                        if (connectedEdges.includes(edge))
                            return { ...edge, style: { ...edge.style, stroke: color.edge, strokeWidth: color.strokeWidth } };

                        return edge;
                    });

                    setEdges(updatedEdges);
                }
            });

            setNodes(updatedNodes1);
        }

        const expandedNodes = ExpandCollapse(updatedNodes1, edges);
        setAllNodes(updatedNodes);
        graph(expandedNodes, edges);
    };

    // NodeClick: Handles click events on nodes, toggling their expanded state and updating styles.
    // Input: node (Object) - the clicked node, color (String) - the color for the node when expanded.
    const NodeClick = (node, color) => {
        fitView({ duration: 400, nodes: [node], padding: 5 });
        const data = node.data.label

        const { edges: connectedEdges } = getNodesAndEdgesConnectedToSource(node.id);

        // Update the style here
        const updatedNodes = allNodes.map((n) => {
            if (n.id === node.id) {
                return {
                    ...n,
                    style: {
                        ...n.style,
                        border: "1px solid black",
                        backgroundColor: node.style.backgroundColor === color ? "white" : color,
                        color: "#000"
                    },
                    data: { ...n.data, expanded: !n.data.expanded }
                };
            }
            return n;
        });

        setAllNodes(updatedNodes);
        const expandedNodes = ExpandCollapse(updatedNodes, edges);

        // Aggiorna lo stile degli edge collegati
        const updatedEdges = edges.map((edge) => {
            if (connectedEdges.includes(edge)) {
                if (edge.target !== node.id) {
                    return {
                        ...edge,
                        style: {
                            ...edge.style,
                            stroke: node.style.backgroundColor === color ? "rgba(177,177,183,255)" : color,
                            strokeWidth: node.style.backgroundColor === color ? "1.3" : 3,
                        }
                    };
                }
                return {
                    ...edge,
                    style: {
                        ...edge.style,
                        stroke: edge.style.stroke === color ? "rgba(177,177,183,255)" : color,
                        strokeWidth: edge.style.strokeWidth === 3 ? "1.3" : 3,
                    }
                };
            }
            return edge;
        });

        graph(expandedNodes, updatedEdges)

        if (node.data.expandable === false) {
            if (node.type !== undefined) onNodeClick(url, color, node);
            else onNodeClick(node.data.text || data, color, node);
        }
    }

    return (
        <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={params => setEdges(eds => addEdge({ ...params, type: ConnectionLineType.SmoothStep, animated: true }, eds))}
            fitView
            connectionLineType={ConnectionLineType.SmoothStep}
            onNodeClick={(event, node) => NodeClick(node, "rgba(191, 230, 207,255)")}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            proOptions={proOptions}
            style={{ background: "white", borderRadius: "2%" }}
        >
            <Background />
            <MiniMap zoomable pannable className="minimap" />
            <Controls className="controls" />
        </ReactFlow >
    );
});

export default PDFStructure;