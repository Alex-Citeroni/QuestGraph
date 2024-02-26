import fitz
import os
import shutil
import base64
from utils import (
    download_pdf_from_url,
    process_page,
    process_image,
    get_title,
    change_structure,
)
from firebase_operations import upload_images_to_firebase
from mongo_db_operations import load_url, mongo_load_data
from openai_operations import nodes_and_edges, generate_index
from index_search import find_top_similarities
from logger import logger

# Constants
TARGET_KEYWORDS = [
    "INDEX",
    "TABLE OF CONTENTS",
    "argument",
    "CONTENTS",
    "SUMMARY",
    "LIST",
    "FIGURES",
]


def elabora_dati(file_name: str, download_url: str):
    """
    Process data from a PDF file, including downloading, extracting images, identifying the index pages,
    and generating a structured JSON representation.

    Parameters:
    - file_name (str): The name of the PDF file.
    - download_url (str): The URL from which to download the PDF.

    Returns:
    - None
    """
    # Log the start of data processing
    logger.info(f"Processing data: {file_name, download_url}")

    # Download the PDF file
    download_pdf_from_url(download_url, file_name)
    logger.info("File downloaded!")

    # Open the PDF document
    pdf_document = fitz.open(file_name)
    pdf_whitout_extension = os.path.splitext(file_name)[0]
    pdf_folder = os.path.join(os.getcwd(), pdf_whitout_extension)
    os.makedirs(pdf_folder, exist_ok=True)
    logger.info("Folder created successfully!")

    # Process each page of the PDF, saving it as an image
    for page_num in range(len(pdf_document)):
        process_page(pdf_document, page_num, pdf_folder)
    logger.info("Pages transformed into images")

    # Identify index pages using predefined keywords
    similarities = find_top_similarities(file_name, TARGET_KEYWORDS)
    index_pages = [tupla[0] for tupla in similarities]
    index_pages.sort()
    logger.info(f"Identified index pages: {index_pages}")

    # Extract images for GPT4-Vision processing
    logger.info("Extracting images for GPT4-Vision")
    image_blocks = []
    for page_num in index_pages:
        image_folder = f"{pdf_folder}/page_{page_num}.png"
        with open(image_folder, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            image_blocks.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            )

    # Call GPT4-Vision to process images
    logger.info("Calling GPT4-Vision")
    message_text = """
                    You are an expert in recognizing the indices of a PDF. You will be provided with various images of a PDF, and your task is to identify which of these images represent an index of that PDF. Pay attention because an index may be distributed across multiple pages. Once the index is identified, make sure it does not continue onto the following pages.

                    Ensure that you have identified all the associated chapter titles and page numbers.
                    Do not make up words, titles, or page numbers, but ensure they are exactly as they appear.
                    Do not add comments.
                    The JSON you need to construct should have the following characteristics:

                    Title and associated starting page

                    The JSON should have this format.

                    {
                    "tableOfContents": [
                        { "title": “...”, "page": … },
                        { "title": “...”, "page": … },
                        { "title": “...”, "page": … },
                    ]
                    }

                    Return only the "index" JSON.
                    Do not include the markdown "" or "json" at the beginning or end.
                    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message_text,
                },
            ],
        }
    ]
    messages[0]["content"].extend(image_blocks)

    # Generate index using GPT4-Vision
    result_json = generate_index(messages)

    # Generate JSON structure
    json_structure = {pdf_whitout_extension: result_json}
    logger.info("Indice creato con successo")

    # Upload images to Firebase
    image_urls_dict = upload_images_to_firebase(pdf_whitout_extension)
    logger.info("Immagini caricate su Firebase")

    # Process images using OCR (Optical Character Recognition)
    image_files = [
        file for file in os.listdir(pdf_whitout_extension) if file.endswith((".png"))
    ]
    image_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))

    all_blueprints = {}
    for image_file in image_files:
        page, _ = os.path.splitext(image_file)
        image_path = os.path.join(pdf_whitout_extension, image_file)
        logger.info(f"OCR su {image_path}")
        blueprint = process_image(image_path, r"-l eng")
        all_blueprints[page] = blueprint
    logger.info("Images extracted from the PDF")

    # Create introduction pages
    introduction_dict = {}
    for page_num in range(
        1, json_structure[pdf_whitout_extension]["index"]["chapter 1"]["page"]
    ):
        page_key = f"page_{page_num}"
        introduction_page = all_blueprints[page_key]

        # Add image URLs if available for this page
        if page_num in image_urls_dict:
            introduction_page["images"] = image_urls_dict[page_num]

        introduction_dict[page_key] = introduction_page

    json_structure[pdf_whitout_extension]["Introduction"] = introduction_dict

    # Create dictionary for chapters and pages
    for chapter_number, chapter_info in json_structure[pdf_whitout_extension][
        "index"
    ].items():
        chapter_key = chapter_info["title"]
        start_page = chapter_info["page"]

        # Extract chapter number from the key
        parts = chapter_number.split(" ")
        number_of_chapter = int(parts[1])

        # Calculate end page based on the next chapter or the last page of the document
        if (
            f"chapter {number_of_chapter + 1}"
            in json_structure[pdf_whitout_extension]["index"]
        ):
            end_page = (
                json_structure[pdf_whitout_extension]["index"][
                    f"chapter {number_of_chapter + 1}"
                ]["page"]
                - 1
            )
        else:
            end_page = len(pdf_document)

        logger.info(
            f"Chapter {number_of_chapter}: Start Page - {start_page}, End Page - {end_page}"
        )

        # Create dictionary for pages
        pages_dict = {}
        for page_num in range(start_page, end_page + 1):
            page_key = f"page_{page_num}"
            page_content = all_blueprints[page_key]

            # Add image URLs if available for this page
            if page_num in image_urls_dict:
                page_content["images"] = image_urls_dict[page_num]

            pages_dict[page_key] = page_content
        json_structure[pdf_whitout_extension][chapter_key] = pages_dict

    logger.info("JSON structure created!")

    # Generate block titles and save the JSON to file and Firebase
    structure, url = get_title(json_structure)

    # Load URLs to MongoDB
    load_url(pdf_whitout_extension, url)

    # Modify the structure of the JSON file for loading into MongoDB
    new_structure = change_structure(structure)

    # Generate nodes and edges using ChatGPT
    mongo_data = nodes_and_edges(new_structure)

    # Load everything into MongoDB
    mongo_load_data(mongo_data)

    # Close the PDF document
    pdf_document.close()

    # Delete PDF files, folders, and their contents
    try:
        os.remove(file_name)
        os.remove(pdf_whitout_extension + ".json")
        logger.info(f"Files {pdf_whitout_extension} successfully deleted.")
        shutil.rmtree(pdf_whitout_extension)
        shutil.rmtree(pdf_whitout_extension + "_images")
        logger.info(f"Folders {pdf_whitout_extension} successfully deleted.")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
