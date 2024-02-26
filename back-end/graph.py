initial_start_page_value = []


def create_handle_node(
    id: str, data: str, url: str, lista: list, tipi: list, expanded: bool
):
    """
    Create a 'handle' node and add it to the lists if it doesn't already exist.

    Args:
        id (str): Unique identifier for the node.
        data (str): Node label.
        url (str): URL associated with the node.
        list (list): List of nodes.
        types (list): List of node types.

    Returns:
        None
    """
    node = {
        "id": id,
        "data": {"label": data},
        "type": id,
        "style": {
            "expanded": expanded,
            "border": "1px solid black",
            "backgroundColor": "white",
            "color": "black",
        },
    }

    nodeType = {id: url}

    # Check if the node type already exists in the list before adding it
    if nodeType not in tipi:
        tipi.append(nodeType)

    # Check if the node already exists in the list before adding it
    if node not in lista:
        lista.append(node)


def create_node(
    id: str,
    data: str,
    order: float,
    lista: list,
    page: int,
    section: str,
    expanded: bool,
):
    """
    Create a node and add it to the list if it doesn't already exist.
    Create a node and add it to the list if it doesn't already exist.

    Args:
        id (str): Unique identifier for the node.
        data (str): Node label.
        order (float): Node order.
        list (list): List of nodes.
        page (int): Page number.
        section (str): Node section.
        id (str): Unique identifier for the node.
        data (str): Node label.
        order (float): Node order.
        list (list): List of nodes.
        page (int): Page number.
        section (str): Node section.

    Returns:
        None
    """
    node = {
        "id": id,
        "data": {
            "label": data,
            "expanded": expanded,
            "order": order,
            "page": page,
            "section": section,
        },
        "style": {
            "border": "1px solid black",
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "16px",
        },
    }

    # Check if the node already exists in the list before adding it
    if node not in lista:
        lista.append(node)


def create_paragraph_node(
    id: str,
    data: str,
    text: str,
    section: str,
    page: int,
    lista: list,
    order: float,
    expanded: bool,
):
    """
    Create a 'paragraph' node and add it to the list if it doesn't already exist.

    Args:
        id (str): Unique identifier for the node.
        data (str): Node label.
        text (str): Text associated with the node.
        section (str): Document section.
        page (int): Page number.
        list (list): List of nodes.
        order (float): Node order.

    Returns:
        None
    """
    node = {
        "id": id,
        "data": {
            "label": data,
            "text": text,
            "section": section,
            "page": page,
            "order": order,
            "expanded": expanded,
        },
        "style": {
            "border": "1px solid black",
            "backgroundColor": "white",
            "color": "black",
        },
    }

    # Check if the node already exists in the list before adding it
    # Check if the node already exists in the list before adding it
    if node not in lista:
        lista.append(node)


def create_edge(id: str, source: str, target: str, label: str, lista: list):
    """
    Create an edge and add it to the list if it doesn't already exist.

    Args:
        id (str): Unique identifier for the edge.
        source (str): Source node of the edge.
        target (str): Target node of the edge.
        label (str): Edge label.
        list (list): List of edges.

    Returns:
        None
    """
    edge = {
        "id": id,
        "source": source,
        "target": target,
        "label": label,
        "type": "smoothstep",
        "style": {"stroke": "rgba(177,177,183,255)", "strokeWidth": 1.3},
    }

    # Check if the edge already exists in the list before adding it
    # Check if the edge already exists in the list before adding it
    if edge not in lista:
        lista.append(edge)


def process_document(doc: dict, structure: dict, members: dict):
    """
    Process a document and update the structure and members.

    Args:
        doc (dict): Document data.
        structure (dict): Document structure.
        members (dict): Document members.

    Returns:
        None
    """
    pdf_title = doc["pdf"]
    index = "Index"
    introduction = "Introduction"
    start_page_value = doc.get("start_page", 0)
    chapter = doc.get("chapter", None)
    images = doc.get("images", None)
    page = str(doc.get("page", None))
    phrases = doc.get("phrases", None)
    section = doc.get("section", None)

    if pdf_title not in structure:
        structure[pdf_title] = {"initialNodes": [], "initialEdges": []}

    if pdf_title not in members:
        members[pdf_title] = {}

    initial_nodes = structure[pdf_title]["initialNodes"]
    initial_edges = structure[pdf_title]["initialEdges"]

    block_nodes_edges = members[pdf_title]

    if "Images" not in structure[pdf_title]:
        structure[pdf_title]["Images"] = {
            "imgNodes": [],
            "imgEdges": [],
            "nodeTypes": [],
        }

    imgNodes = structure[pdf_title]["Images"]["imgNodes"]
    imgEdges = structure[pdf_title]["Images"]["imgEdges"]
    nodeTypes = structure[pdf_title]["Images"]["nodeTypes"]

    # Save the initial value of start_page_value
    initial_start_page_value.append(start_page_value)

    create_node(pdf_title, pdf_title, 0, initial_nodes, 0, pdf_title, True)  # PDF
    create_node(
        index, index, 0.1, initial_nodes, initial_start_page_value[0], index, False
    )  # Index
    create_edge(pdf_title + index, pdf_title, index, "", initial_edges)  # PDF - Index
    create_node(
        introduction, introduction, 0.2, initial_nodes, 1, introduction, False
    )  # Introduction
    create_edge(
        pdf_title + introduction, pdf_title, introduction, "", initial_edges
    )  # PDF - Introduction

    if chapter:
        title = doc["title"]
        node_id = str(chapter) + title
        create_node(
            node_id, title, chapter, initial_nodes, start_page_value, title, False
        )  # Chapters index
        create_edge(
            index + node_id, index, node_id, "", initial_edges
        )  # Index - Chapter
        create_node(
            title, title, chapter, initial_nodes, start_page_value, title, False
        )  # Chapters PDF
        create_edge(
            pdf_title + title, pdf_title, title, "", initial_edges
        )  # PDF - Chapter

    if phrases:
        for phrase in phrases:
            block_number = phrase["block_number"]
            page_block = page + "_" + str(block_number)
            block_title = phrase["block_title"]
            block_text = phrase["block_text"]
            number_part = 1

            # Check if the block with the same title already exists
            existing_block = next(
                (
                    node
                    for node in initial_nodes
                    if node["data"]["label"] == block_title
                    and "text" in node["data"]
                    and section == node["data"]["section"]
                ),
                None,
            )

            if existing_block:
                # If the block exists, append the new text to its existing text
                block_id = page_block + "_" + str(number_part)
                existing_block["data"]["label"] += f" (part {number_part})"
                number_part += 1
                create_paragraph_node(
                    block_id,
                    block_title + f" (part {number_part})",
                    block_text,
                    section,
                    int(page),
                    initial_nodes,
                    block_number,
                    False,
                )  # Block
                create_edge(
                    section + block_id,
                    section,
                    block_id,
                    "",
                    initial_edges,
                )  # Chapter - Block

            else:
                # If the block doesn't exist, create a new block
                create_paragraph_node(
                    page_block,
                    block_title,
                    block_text,
                    section,
                    int(page),
                    initial_nodes,
                    block_number,
                    False,
                )  # Block
                create_edge(
                    section + page_block, section, page_block, "", initial_edges
                )  # Chapter - Block

            initialEdges = phrase.get("initialEdges", None)
            initialNodes = phrase.get("initialNodes", None)

            if initialNodes:
                if page_block not in block_nodes_edges:
                    block_nodes_edges[page_block] = {
                        "initialNodes": [],
                        "initialEdges": [],
                    }
                block_nodes_edges[page_block]["initialNodes"] = initialNodes
                block_nodes_edges[page_block]["initialEdges"] = initialEdges

    if images:
        for img in images:
            create_handle_node(page + img, page, img, imgNodes, nodeTypes, False)
            create_edge(page + "_" + img, section, page + img, "", imgEdges)


def sort_and_merge_nodes_and_edges(pdf_data: dict):
    """
    Sort and merge the nodes and edges of the PDF document.

    Args:
        pdf_data (dict): PDF document data.
        pdf_data (dict): PDF document data.

    Returns:
        None
    """

    # Separate nodes with the "page" key and those without
    nodes_with_page = [
        node for node in pdf_data["initialNodes"] if "page" in node["data"]
    ]

    # Sort nodes with "page"
    pdf_data["initialNodes"] = sorted(
        nodes_with_page, key=lambda x: (x["data"]["page"], x["data"]["order"])
    )

    # Get a map of node IDs to their indices in the list
    node_id_to_index = {
        node["id"]: index for index, node in enumerate(pdf_data["initialNodes"])
    }

    # Sort edges based on the indices of the source and target nodes
    pdf_data["initialEdges"] = sorted(
        pdf_data["initialEdges"],
        key=lambda edge: (
            node_id_to_index[edge["source"]],
            node_id_to_index[edge["target"]],
        ),
    )
