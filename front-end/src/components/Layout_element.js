import dagre from 'dagre';
import { Position } from 'reactflow';

const NODE_WIDTH = 172;
const NODE_HEIGHT = 36;

export function getLayoutedElements(nodes, edges, direction = 'TB') {
    const dagreGraph = createDagreGraph(nodes, edges, direction);
    dagre.layout(dagreGraph);

    nodes.forEach(node => {
        const nodeWithPosition = dagreGraph.node(node.id);
        const isHorizontal = direction === 'LR';

        node.targetPosition = isHorizontal ? 'left' : 'top';
        node.sourcePosition = isHorizontal ? 'right' : 'bottom';
        node.position = {
            x: nodeWithPosition.x - NODE_WIDTH / 2,
            y: nodeWithPosition.y - NODE_HEIGHT / 2
        };

        return node;
    });

    return { nodes, edges };
}

function createDagreGraph(nodes, edges, direction) {
    const dagreGraph = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

    dagreGraph.setGraph({ rankdir: direction });
    nodes.forEach(node => dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT }));
    edges.forEach(edge => dagreGraph.setEdge(edge.source, edge.target));

    return dagreGraph;
}

export function getLayoutedElementsPDF(nodes, edges) {
    const dagreGraph = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

    dagreGraph.setGraph({ rankdir: "TB" });

    const horizontalSpacing = 20;  // Regola questo valore per cambiare la distanza orizzontale tra i nodi
    const verticalSpacing = 85;

    nodes.forEach(node => dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT }));
    edges.forEach(edge => dagreGraph.setEdge(edge.source, edge.target));

    // Identifica l'id del nodo padre
    const parentNodeId = nodes[0].id;

    // Calcola la posizione desiderata del primo nodo
    const firstNodeX = 0;

    // Divide i nodi in quelli con la stessa sorgente del nodo padre e quelli con una sorgente diversa
    const parentSourceNodes = [];
    const childNodes = [];
    const grandchildNodes = [];

    nodes.forEach((node, index) => {
        if (index === 0) {
            parentSourceNodes.push(node);
        } else if (edges.some(edge => edge.source === parentNodeId && edge.target === node.id)) {
            childNodes.push(node);
        } else if (edges.some(edge => childNodes.map(child => child.id).includes(edge.source) && edge.target === node.id)) {
            grandchildNodes.push(node);
        }
    });

    // Salvare i grandchildNodes in base ai childNodes in un dizionario
    const grandchildNodesDict = grandchildNodes.reduce((dict, grandchild) => {
        const parentChildNode = childNodes.find(child => edges.some(edge => edge.source === child.id && edge.target === grandchild.id));
        if (parentChildNode) {
            if (!dict[parentChildNode.id]) {
                dict[parentChildNode.id] = [];
            }

            const childNodeIndex = childNodes.findIndex(node => node.id === parentChildNode.id);
            const xPosition = firstNodeX + 2 * (NODE_WIDTH + horizontalSpacing);

            // Calcola la posizione y in base al numero di grandchild precedenti dello stesso childNode
            const yPositionBase = childNodeIndex * (NODE_HEIGHT + verticalSpacing) + 100;
            const yPosition = yPositionBase + dict[parentChildNode.id].length * verticalSpacing;  // Incrementa la posizione y per ogni grandchild aggiunto

            dict[parentChildNode.id].push({
                ...grandchild,
                position: { x: xPosition, y: yPosition, childNodeIndex },
                sourcePosition: Position.Right,
                targetPosition: Position.Left,
            });
        }
        return dict;
    }, {});

    // Calcola la posizione aggiuntiva y per i childNodes in base ai loro grandchildNodes
    const childNodesYAdjustment = childNodes.map(childNode => {
        if (grandchildNodesDict[childNode.id] && grandchildNodesDict[childNode.id].length > 0) {
            return grandchildNodesDict[childNode.id].length * 130;  // Aumento in base al numero di grandchildNodes
        }
        return 0;
    });

    // Imposta la posizione di ogni nodo
    return [
        ...parentSourceNodes.map((node, index) => ({
            ...node,
            position: { x: firstNodeX, y: index * (NODE_HEIGHT + verticalSpacing) },
            sourcePosition: Position.Right,
            targetPosition: Position.Left,
        })),
        ...childNodes.map((node, index) => {
            const yPosition = index * (NODE_HEIGHT + verticalSpacing) + childNodesYAdjustment.slice(0, index).reduce((a, b) => a + b, 0);

            // Aggiorna anche la posizione y dei grandchildNodes di questo childNode
            if (grandchildNodesDict[node.id]) {
                grandchildNodesDict[node.id].forEach((grandchild, grandchildIndex) => {
                    grandchild.position.y = yPosition + 100 + grandchildIndex * 130;
                });
            }

            return {
                ...node,
                position: { x: firstNodeX + NODE_WIDTH + horizontalSpacing, y: yPosition + 80 },
                sourcePosition: Position.Right,
                targetPosition: Position.Left,
            };
        }),
        // Aggiungi i grandchildNodes con la posizione y aggiornata
        ...grandchildNodes.flatMap(grandchild => {
            const parentChildNode = childNodes.find(childNode => childNode.id === edges.find(edge => edge.target === grandchild.id)?.source);
            if (parentChildNode) {
                const grandchildInfo = grandchildNodesDict[parentChildNode.id].find(info => info.id === grandchild.id);
                if (grandchildInfo) {
                    return {
                        ...grandchild,
                        position: grandchildInfo.position,
                        sourcePosition: Position.Right,
                        targetPosition: Position.Left,
                    };
                }
            }
            return [];
        }),
    ];
}