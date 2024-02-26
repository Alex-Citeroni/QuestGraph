from openai import OpenAI
import re
import json
import ast
from logger import logger
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()

# Constants for API Key
OPENAI_API_KEY = os.getenv("GPT_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

total_input_tokens_gpt_4 = 0
total_output_tokens_gpt_4 = 0
total_input_tokens_gpt_3_5 = 0
total_output_tokens_gpt_3_5 = 0


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# Function for calling the Chat GPT API
def call_chat_gpt(text: str):
    """
    Send a request to GPT-4-turbo to associate an appropriate title with a text block.
    Returns a JSON indicating whether a title is present in the text block and, if so,
    what the title is. The response follows the provided examples.

    Args:
        text (str): The text block to base the request on.

    Returns:
        dict: A dictionary containing information about the title in the text block.
              - 'containTitle': True if a title is present, False otherwise.
              - 'title': The title associated with the text block, or "None" if not present.
    """

    # Reference the global variable
    global total_input_tokens_gpt_4, total_output_tokens_gpt_4

    prompt = f"""
          You have a text block available in the request.
          Return a JSON that indicates whether a title is present in the text block, and if so, what the title is.
          Do not invent titles and respond as in the attached examples.
          REQUEST: '{text}'
          """

    example = """
        EXAMPLE - 1
        TEXT:
        ‘FOREWORD
        Among the great challenges posed to democracy today is the use of technology, data, and automated systems in
        ways that threaten the rights of the American public. Too often, these tools are used to limit our opportunities and
        prevent our access to critical resources or services. These problems are well documented. In America and around
        the world, systems supposed to help with patient care have proven unsafe, ineffective, or biased. Algorithms used
        in hiring and credit decisions have been found to reflect and reproduce existing unwanted inequities or embed
        new harmful bias and discrimination. Unchecked social media data collection has been used to threaten people’s
        opportunities, undermine their privacy, or pervasively track their activity—often without their knowledge or
        consent.’

        ANSWER:
        {
          "containTitle": true,
          "title": "FOREWORD"
        }

        EXAMPLE – 2
        TEXT:
        ‘These outcomes are deeply harmful—but they are not inevitable. Automated systems have brought about extraordinary benefits, from technology that helps farmers grow food more efficiently and computers that predict storm
        paths, to algorithms that can identify diseases in patients. These tools now drive important decisions across
        sectors, while data is helping to revolutionize global industries. Fueled by the power of American innovation,
        these tools hold the potential to redefine every part of our society and make life better for everyone.’

        ANSWER:
        {
          "containTitle": false,
          "title": "None"
        }
        """

    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant to read text and associate an appropriate title with it, you have a text block available in the request. Return a JSON that indicates whether a title is present in the text block, and if so, what the title is. Do not invent titles and respond as in the attached examples.",
            },
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": example},
        ],
    )

    # Calcola e registra i token in input
    input_tokens = num_tokens_from_string(prompt, "cl100k_base")
    total_input_tokens_gpt_4 += input_tokens
    logger.info(f"Token in input: {input_tokens}")
    logger.info(f"GPT4 Total input tokens: {total_input_tokens_gpt_4}")

    # Extracting the response from the API call
    res = completion.choices[0].message.content

    print(res)

    # Calcola e registra i token in output
    output_tokens = num_tokens_from_string(res, "cl100k_base")
    total_output_tokens_gpt_4 += output_tokens
    logger.info(f"Token in output: {output_tokens}")
    logger.info(f"GPT4 Total output tokens: {total_output_tokens_gpt_4}")

    # Removing prefixes and suffixes
    cleaned_response = res.replace("```json", "").replace("```", "").strip()

    # Remove non-printable characters
    cleaned_response = re.sub(r"[^\x20-\x7E]", "", cleaned_response)

    # Load JSON
    final = json.loads(cleaned_response)

    # Returning the complete response
    return final


def node_load(python_dict_text: list):
    """
    Load initial nodes from a textual representation of a dictionary and return a list
    of desired nodes in the required format.

    Args:
        python_dict_list (list): A list of dictionaries containing information about nodes.

    Returns:
        list: A list of desired nodes in the format:
              [
                {"id": "label1", "data": {"label": "label1"}},
                {"id": "label2", "data": {"label": "label2"}},
                ...
              ]
    """

    # List for desired nodes
    desired_nodes = []

    # Iterate over the initial nodes and create desired nodes
    for node in python_dict_text:
        label = node["label"]
        desired_node = {"id": label, "data": {"label": label}}

        # Add the node to the list
        desired_nodes.append(desired_node)

    # Return the list of desired nodes
    return desired_nodes


def process_nodes(pdf_text: str):
    """
    Extracts and processes initial nodes from a textual representation associated with a PDF.

    Args:
        pdf_text (str): A string containing the text associated with the initial nodes.

    Returns:
        list: A list of desired nodes in the format required for building a graph.
    """
    try:
        # Try to load the text as JSON
        data = json.loads(pdf_text)
        if "initialNodes" in data:
            # Process the initial nodes if they are found in the JSON
            return node_load(data["initialNodes"])
    except json.JSONDecodeError:
        # Search for the match of the initial nodes definition in the text
        match = re.search(r"initialNodes[\s:=]+(\[.*?\]);", pdf_text, re.DOTALL)

        if match:
            # If a match is found, extract the part of the text representing the initial nodes
            python_dict_text = match.group(1)
            # Remove any newline characters present in the text
            python_dict_text = python_dict_text.replace("\\n", "")
            # Evaluate the textual representation of the Python dictionary
            python_dict_text = ast.literal_eval(python_dict_text)
            # Call the function to load and format the nodes
            return node_load(python_dict_text)
        else:
            # Initialize initial_nodes_start to an invalid value
            initial_nodes_start = -1

            # If a direct match is not found, look for alternatives in the text
            initial_nodes_start_colon = pdf_text.find("initialNodes:")
            initial_nodes_start_equal = pdf_text.find("initialNodes =")

            # Determine the starting point of the initial nodes definition
            if initial_nodes_start_colon != -1 and initial_nodes_start_equal != -1:
                initial_nodes_start = min(
                    initial_nodes_start_colon, initial_nodes_start_equal
                )
            elif initial_nodes_start_colon != -1:
                initial_nodes_start = initial_nodes_start_colon
            elif initial_nodes_start_equal != -1:
                initial_nodes_start = initial_nodes_start_equal
            else:
                logger.error(f"No match for initialNodes 1:\n{pdf_text}")

            if initial_nodes_start != -1:
                # If a starting position is found, look for the end of the initial nodes definition
                initial_nodes_start = pdf_text.find("[", initial_nodes_start)
                initial_nodes_end = pdf_text.find("]", initial_nodes_start) + 1
                # Extract the part of the text representing the initial nodes
                initial_nodes_text = pdf_text[initial_nodes_start:initial_nodes_end]
                # Remove any newline characters present in the text
                python_dict_text = initial_nodes_text.replace("\\n", "")
                # Call the function to load and format the nodes
                return node_load(python_dict_text)
            else:
                logger.error(f"No match for initialNodes 2:\n{pdf_text}")


def edge_load(edge_objects: list):
    """
    Load and format edge objects from a textual representation in JSON format.

    Args:
        edge_objects (list): A list of strings containing edge objects in JSON format.

    Returns:
        list: A list of desired edge objects in the format required for building a graph.
    """

    # Initialize an empty list for desired edges
    desired_edges = []

    # Iterate through the edge objects in the list
    for edge_text in edge_objects:
        # Create a dictionary to store edge data
        edge_data = {
            item.split(":")[0].strip().strip('"'): item.split(":")[1].strip().strip('"')
            for item in re.findall(r'"[^"]+"\s*:\s*"[^"]+"', edge_text)
        }

        # Add an "id" field by concatenating the source and target nodes
        edge_data["id"] = edge_data["source"] + "_" + edge_data["target"]

        # Add an "animated" field with the value "true"
        edge_data["animated"] = "true"

        # Add the edge dictionary to the desired list
        desired_edges.append(edge_data)

    # Return the list of desired edges
    return desired_edges


def edge_load_json(edge_objects: list):
    """
    Load and format edge objects from a list of dictionaries.

    Args:
        edge_objects (list): A list of dictionaries containing edge objects.

    Returns:
        list: A list of desired edge objects in the format required for building a graph.
    """

    # Initialize an empty list for desired edges
    desired_edges = []

    # Iterate through the edge objects in the list
    for edge_data in edge_objects:
        # Check if the required keys are in the dictionary
        if all(key in edge_data for key in ["source", "target", "label"]):
            # Add an "id" field by concatenating the source and target nodes
            edge_data["id"] = edge_data["source"] + "_" + edge_data["target"]

            # Add an "animated" field with the value "true"
            edge_data["animated"] = "true"

            # Add the edge dictionary to the desired list
            desired_edges.append(edge_data)
        else:
            # Log an error or handle the missing key(s)
            logger.error(f"Missing required keys in edge data: {edge_data}")

    # Return the list of desired edges
    return desired_edges


def process_edges(pdf_text: str):
    """
    Extract and process edge objects from a textual representation of the graph.

    Args:
        pdf_text (str): The text containing the representation of the graph, often from a PDF file.

    Returns:
        list: A list of edge objects in the format required for building a graph.
    """
    try:
        # Try to load the text as JSON
        data = json.loads(pdf_text)
        if "initialEdges" in data:
            # Process the initial edges if they are found in the JSON
            return edge_load_json(data["initialEdges"])
    except json.JSONDecodeError:
        # Search for the match of the edge representation in the text
        match = re.search(r"initialEdges[\s:=]+(\[.*?\]);", pdf_text, re.DOTALL)

        # If a match is found
        if match:
            # Extract the part of the text containing the edge representation
            javascript_text_edge = match.group(1)

            # Find all edge objects in the representation
            edge_objects = re.findall(r"\{[^{}]*\}", javascript_text_edge)

            # Call the function to load and format edge objects
            return edge_load(edge_objects)
        else:
            # Initialize initial_edges_start to an invalid value
            initial_edges_start = -1

            # If a direct match is not found, look for other possible indications in the text
            initial_edges_start_colon = pdf_text.find("initialEdges:")
            initial_edges_start_equal = pdf_text.find("initialEdges =")

            # Find the starting position of the edge information
            if initial_edges_start_colon != -1 and initial_edges_start_equal != -1:
                initial_edges_start = min(
                    initial_edges_start_colon, initial_edges_start_equal
                )
            elif initial_edges_start_colon != -1:
                initial_edges_start = initial_edges_start_colon
            elif initial_edges_start_equal != -1:
                initial_edges_start = initial_edges_start_equal
            else:
                # If no indications for edges are found, log the error
                logger.error(f"Nessuna corrispondenza per initialEdges 1:\n{pdf_text}")

            # If the starting position is found, extract and process edge objects
            if initial_edges_start != -1:
                initial_edges_start = pdf_text.find("[", initial_edges_start)
                initial_edges_end = pdf_text.find("]", initial_edges_start) + 1
                initial_edges_text = pdf_text[initial_edges_start:initial_edges_end]
                python_dict_text = initial_edges_text.replace("\n", "")
                edge_objects = re.findall(r"\{[^{}]*\}", python_dict_text)
                return edge_load(edge_objects)
            else:
                # If no indications for edges are found, log the error
                logger.error(f"Nessuna corrispondenza per initialEdges 2:\n{pdf_text}")


def nodes_and_edges(new_structure: dict):
    """
    Build nodes and edges for each text block within a data structure representing the content of PDF files.

    Args:
        new_structure (dict): A data structure containing the content extracted from PDF files, organized by text blocks and sentences.

    Returns:
        dict: The updated data structure with information about the nodes and edges created for each text block.
    """

    global total_input_tokens_gpt_3_5, total_output_tokens_gpt_3_5

    # Iterate over the PDFs in the data structure
    for pdf in new_structure:
        # Iterate over the elements of each PDF
        for item in new_structure[pdf]:
            # Check if there are sentences in the element
            if "phrases" in item:
                # Iterate over the sentences of each element
                for phrase in item["phrases"]:
                    # Build a string containing information about the sentence
                    stringa_frasi = f"Given this text from the paragraph '{phrase['block_title']}' of the chapther '{item['section']}' of the '{pdf}' PDF:'\n '{phrase['block_text']}'\nExtract as many meaningful relationships as possible to create a knowledge graph."

                    # Define the prompt for the GPT-3.5-turbo completion request
                    prompt = """
                    You are truly skilled at building knowledge graphs. Your task is to create nodes and edges, meaning relationships; you are an expert in Named Entity Recognition (NER).
                    I want you to write as many meaningful relationships as possible for each block of text you receive.
                    Of course, these relationships must make sense, and please check if you have used the same words and meanings found in the text.
                    The crucial aspect is that just by reading the relationships you create, I should be able to understand the content of the text.
                    Please aim to be as explanatory as possible.

                    Within the 'initialEdges' list, you will find the 'label' tag, inside it, find a word or phrase of up to 10 words that explains why those two nodes have a connection.
                    Make sure the phrase does not contain single or double quotation marks or abbreviations.
                    Every 'source' and every 'target' in initialEdges must also be contained in the initialNodes label.
                    The output must be in JSON format.
                    Just write initialNodes and initialEdges to me as an answer.

                    Return only the JSON.
                    Do not include the markdown "" or "json" at the beginning or end.
                    """

                    example = """
                    The JSON should have this format

                    initialNodes = [
                    {
                        "label": "",
                    },
                    {
                        "label": "",
                    },
                    ];

                    initialEdges = [
                    {
                        "source": "node_name",
                        "target": "node_name",
                        "label": "edge label",
                    },
                    {
                        "source": "node_name",
                        "target": "node_name",
                        "label": "edge label",
                    },
                    ];
                    """

                    frasi = stringa_frasi + prompt

                    # Execute the GPT-3.5-turbo completion request
                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",
                        response_format={"type": "json_object"},
                        temperature=0,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a knowledge graph assistant, skilled in create relation with nodes and edges in JSON format.",
                            },
                            {"role": "user", "content": frasi},
                            {"role": "assistant", "content": example},
                        ],
                    )

                    # Calcola e registra i token in input
                    input_tokens = num_tokens_from_string(frasi, "cl100k_base")
                    total_input_tokens_gpt_3_5 += input_tokens
                    logger.info(f"Token in input: {input_tokens}")
                    logger.info(
                        f"GPT3.5-Turbo Total input tokens: {total_input_tokens_gpt_3_5}"
                    )

                    # Add the result to the list associated with the 'pdf' key
                    result = completion.choices[0].message.content

                    # Calcola e registra i token in output
                    output_tokens = num_tokens_from_string(result, "cl100k_base")
                    total_output_tokens_gpt_3_5 += output_tokens
                    logger.info(f"Token in output: {output_tokens}")
                    logger.info(
                        f"GPT3.5-Turbo Total output tokens: {total_output_tokens_gpt_3_5}"
                    )

                    # Print the result for debugging
                    logger.info(result)

                    # Remove unnecessary indications from the result
                    result = result.replace("json", "").replace("```", "")

                    # Process and update information about nodes
                    initialNodes = process_nodes(result)
                    phrase["initialNodes"] = initialNodes

                    # Process and update information about edges
                    initialEdges = process_edges(result)
                    phrase["initialEdges"] = initialEdges

    # Log the successful creation and saving of nodes and edges
    logger.info("Nodi e Archi creati e salvati con sueccesso pe rtutti i blocchi.")

    # Return the updated data structure
    return new_structure


def generate_index(messages: list):
    """
    Generate an index from text using GPT-4-vision-preview.

    Args:
        messages (list): A list of messages for the GPT-4-vision-preview completion request.

    Returns:
        dict: A dictionary representing the index generated from the information returned by GPT-4-vision-preview.
    """

    # Centralized configuration
    GPT_MODEL = "gpt-4-vision-preview"
    MAX_TOKENS = 4000

    message_str = json.dumps(messages[0])
    input_tokens = num_tokens_from_string(message_str, "cl100k_base")
    logger.info(f"GPT4V Token in input: {input_tokens}")

    # Execute the GPT-4-vision-preview completion request
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )

    # Get the content from the response
    response_content = response.choices[0].message.content

    # Calcola e registra i token in output
    output_tokens = num_tokens_from_string(response_content, "cl100k_base")
    logger.info(f"Token in output: {output_tokens}")

    # Remove "```", "json", and "\n" from the JSON string
    cleaned_json_string = (
        response_content.replace("```", "").replace("json", "").replace("\n", "")
    )

    # Convert the cleaned JSON string to a JSON object
    cleaned_json_object = json.loads(cleaned_json_string)

    # Build the new format for the index
    result_json = {"index": {}}
    for index, entry in enumerate(cleaned_json_object["tableOfContents"]):
        chapter_name = f"chapter {index + 1}"
        result_json["index"][chapter_name] = entry

    # Return the dictionary representing the generated index
    return result_json
