import requests
import fitz
import os
import spacy
import cv2
import pytesseract
import json
from firebase_operations import upload_json_to_firebase
from openai_operations import call_chat_gpt
from logger import logger

# Carica i modelli di SpaCy in inglese
nlp = spacy.load("en_core_web_trf")
nlp_title = spacy.load("en_core_web_md")


def download_pdf_from_url(url: str, save_path: str):
    """
    Download a PDF from the given URL and save it to the specified path.

    Parameters:
    - url (str): The URL of the PDF.
    - save_path (str): The path where the PDF should be saved.
    """
    response = requests.get(url)
    with open(save_path, "wb") as pdf_file:
        pdf_file.write(response.content)


def process_page(doc: fitz.Document, page_num: int, pdf_name: str):
    """
    Process a page of a PDF document, saving the page as an image and extracting images.

    Parameters:
    - doc (fitz.Document): The PyMuPDF document object.
    - page_num (int): The page number to process.
    - pdf_name (str): The name of the PDF file.

    Returns:
    - image_list (list): A list of images extracted from the page.
    """
    # Load the specified page from the document
    page = doc.load_page(page_num)

    # Define a transformation matrix for the image
    matrix = fitz.Matrix(300 / 72.0, 300 / 72.0)

    # Get a pixmap of the page using the specified matrix
    image = page.get_pixmap(matrix=matrix)

    # Save the page image as a PNG file
    image_filename = os.path.join(pdf_name, f"page_{page_num + 1}.png")
    image.save(image_filename, "png")

    # Create a folder for images if it doesn't exist
    image_folder = os.path.join(os.path.dirname(pdf_name), f"{pdf_name}_images")
    os.makedirs(image_folder, exist_ok=True)

    # Extract images from the page
    image_list = page.get_images()

    # Iterate over the images found on the page
    for image_index, img in enumerate(image_list, start=1):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)

        # Convert CMYK image to RGB if necessary
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)

        # Save the image as a PNG in the new folder
        image_filename = os.path.join(
            image_folder, f"page_{page_num + 1}_image_{image_index}.png"
        )
        pix.save(image_filename)
        pix = None

    # Return the list of extracted images
    return image_list


def divide_into_paragraphs(text: str):
    """
    Divide the given text into paragraphs and extracts titles from each paragraph.

    Parameters:
    - text (str): The input text to be processed.

    Yields:
    - str: Titles extracted from the paragraphs.
    """
    # Use SpaCy to tokenize the input text into sentences
    doc = nlp(text)
    paragraphs = [sent.text for sent in doc.sents]

    # Iterate over the paragraphs
    for i, frase in enumerate(paragraphs):
        # Use spaCy to analyze the sentence as a potential title
        doc_title = nlp_title(frase)
        # Extract individual sentences from the analyzed title
        sentences = [sent.text.strip() for sent in doc_title.sents]
        # Yield each extracted title
        for title in sentences:
            yield title


def combine_within_blocks(block_texts: dict):
    """
    Combine sentences within blocks based on specific criteria.

    Parameters:
    - block_texts (dict): Dictionary containing block numbers as keys and lists of sentences as values.

    Returns:
    - dict: Merged block texts with combined sentences.
    """
    merged_block_texts = {}

    for key, value in block_texts.items():
        merged_block_texts[key] = []
        current_sentence = ""

        for sentence in value:
            # Check if the sentence starts with "-", "/", or ";"
            if sentence.startswith(("-", "/", ";")):
                # Combine the sentence with the previous one
                current_sentence = (
                    current_sentence + sentence[0] + sentence[1:].strip()
                ).strip()
            # Check if the previous sentence ends with "-"
            elif current_sentence.endswith("-"):
                # Combine the sentence with the previous one without "-"
                current_sentence = (current_sentence + sentence).strip()
            else:
                # Check if the sentence contains only one character
                if len(sentence.strip()) == 1:
                    # Add the character to the current sentence
                    current_sentence += sentence
                else:
                    # If the sentence doesn't contain only one character, add the current sentence
                    # (if present) and the current sentence to the list of block sentences
                    if current_sentence:
                        merged_block_texts[key].append(current_sentence)
                    current_sentence = sentence

        # Add the last current sentence (if present) to the list of block sentences
        if current_sentence:
            merged_block_texts[key].append(current_sentence)

    return merged_block_texts


def process_image(image_path: str, custom_config: str):
    """
    Process text extraction from an image using Tesseract OCR.

    Parameters:
    - image_path (str): The path to the image file.
    - custom_config (str): Custom configuration for Tesseract OCR.

    Returns:
    - dict: Dictionary containing processed text blocks and paragraphs extracted from the image.
    """
    # Load the image
    image = cv2.imread(image_path)
    # Extract text from the image (perform OCR with Tesseract)
    results = pytesseract.image_to_data(
        image, output_type=pytesseract.Output.DICT, config=custom_config
    )
    logger.info("OCR fatto")
    # Organize results into text blocks and paragraphs
    block_texts = {}
    block_paragraphs = {}

    for i in range(len(results["text"])):
        text = results["text"][i].strip()
        block_num = results["block_num"][i]
        par_num = results["par_num"][i]

        block_texts.setdefault(block_num, [])
        block_paragraphs.setdefault(block_num, [])

        if len(block_paragraphs[block_num]) == par_num:
            block_paragraphs[block_num].append([])

        if text:
            block_texts[block_num].append(text)
            block_paragraphs[block_num][par_num].append(text)

    # Concatenate text blocks
    concatenated_blocks = {}
    current_block = []

    for key, value in block_texts.items():
        current_block.extend(value)
        if len(current_block) >= 10:
            concatenated_blocks[len(concatenated_blocks)] = current_block
            current_block = []

    if current_block:
        if not concatenated_blocks:
            concatenated_blocks[len(concatenated_blocks)] = current_block
        else:
            last_block_index = max(concatenated_blocks.keys())
            concatenated_blocks[last_block_index].extend(current_block)

    # Convert concatenated blocks into a dictionary
    new_block_texts = {}
    for block_index, concatenated_text in concatenated_blocks.items():
        new_block_texts[block_index] = concatenated_text

    # Combine blocks with sentences starting with a lowercase letter
    merged_block_texts = {}
    previous_key = None
    for key, value in new_block_texts.items():
        if key == 0:
            previous_key = key
            merged_block_texts[key] = value
        elif key > 0:
            if value and value[0][0].islower():
                merged_block_texts[previous_key] += value
            else:
                previous_key = key
                merged_block_texts[key] = value

    # Create a dictionary for the results
    result_dict = {}

    # Iterate over each key-value pair in merged_block_texts
    for block_num, block_text in merged_block_texts.items():
        if block_text:
            combined_text = " ".join(block_text)
            paragraphs = divide_into_paragraphs(combined_text)
            combined_within_block = combine_within_blocks({0: paragraphs})
            result_dict[f"block {block_num}"] = combined_within_block[0]
    return result_dict


def get_title(json_structure: dict):
    """
    Process the textual content from blocks in a JSON structure, extract titles using Chat GPT, and save the results.

    Parameters:
    - json_structure (dict): The JSON structure containing textual content.

    Returns:
    - tuple: A tuple containing the processed data and the URL after uploading the data to Firebase.
    """
    data = json_structure

    # Extract textual content from blocks
    for pdf_title, pdf in data.items():
        title = pdf_title
        for chapter_title, chapter_content in pdf.items():
            if chapter_title != "index":
                previous_block_number = None
                previous_block_title = None
                for page_number, page_content in chapter_content.items():
                    previous_block_text = None
                    new_block = {}
                    for block_number, text in page_content.items():
                        if "images" in block_number:
                            new_block["images"] = text
                        if "images" not in block_number:
                            block_text = " ".join(text)
                            if block_text.strip():
                                # Call Chat GPT API
                                api_response = call_chat_gpt(text)
                                if api_response.get(
                                    "containTitle", False
                                ) or api_response.get("containsTitle", False):
                                    new_block[block_number] = {
                                        "title": api_response["title"],
                                        "text": block_text,
                                    }

                                    # Update the text of the previous block
                                    previous_block_text = block_text
                                    previous_block_number = block_number
                                    previous_block_title = api_response["title"]
                                else:
                                    # If the current block has 'containTitle' False, concatenate the text to the previous block
                                    if previous_block_text is not None:
                                        previous_block_text += " " + block_text
                                        new_block[previous_block_number] = {
                                            "title": previous_block_title,
                                            "text": previous_block_text,
                                        }
                                    else:
                                        # If there is no previous block, add the text as a standalone block
                                        new_block[block_number] = {
                                            "title": previous_block_title,
                                            "text": block_text,
                                        }
                                        # Update the text of the previous block
                                        previous_block_text = block_text
                                        previous_block_number = block_number

                    data[pdf_title][chapter_title][page_number] = new_block

    # Save the JSON string to a file
    with open(f"{title}.json", "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(data, indent=2, ensure_ascii=False))

    logger.info("File JSON salvato con successo.")

    # Upload the file to Firebase
    url = upload_json_to_firebase(f"{title}.json")

    return data, url


def change_structure(structure: dict):
    """
    Convert the structure of a document into a new format.

    Parameters:
    - structure (dict): The original structure of the document.

    Returns:
    - dict: A dictionary containing the transformed document structure.
    """
    documents = {}

    for pdf_file in structure.keys():
        for chapter, page_content in structure[pdf_file].items():
            if chapter == "index":
                for page, page_c in page_content.items():
                    title = page_c["title"]
                    document = {
                        "pdf": pdf_file,
                        "chapter": int(page.split(" ")[1]),
                        "title": title,
                        "start_page": page_c["page"],
                    }
                    # Add the document to the list
                    documents.setdefault(pdf_file, []).append(document)
            else:
                for page, page_c in page_content.items():
                    page_number = int(page.split("_")[1])

                    # Create a JSON document for the current page
                    document = {
                        "pdf": pdf_file,
                        "page": page_number,
                        "phrases": [],
                        "images": [],
                        "section": chapter,
                    }

                    for block, content in page_c.items():
                        if block.startswith("block"):
                            text = content["text"]
                            title_block = content["title"]
                            if title_block is None:
                                title_block = chapter
                            # Add block information to the document
                            block_info = {
                                "block_title": title_block,
                                "block_text": text,
                                "block_number": int(block.split(" ")[1]),
                            }
                            document["phrases"].append(block_info)

                        elif block.startswith("images"):
                            document["images"].extend(content)

                    # Add the document to the list
                    documents.setdefault(pdf_file, []).append(document)

    logger.info("The structure has been successfully changed!")

    return documents
