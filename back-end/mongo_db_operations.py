from pymongo import MongoClient
from logger import logger
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to the MongoDB database
clientMongoDB = MongoClient(os.getenv("MONGODB_URI"))

# Select the database
db = clientMongoDB["NewTest"]

# Select collections
collection_url = db["new_URL"]
collection_pdf = db["new_PDF"]


def mongo_load_data(mongo_data: dict):
    """
    Load data into MongoDB.

    Args:
        mongo_data (dict): Data to be loaded, organized as a dictionary of lists of documents.

        Returns:
            None
    """
    documents_to_insert = []

    for pdf_file, pdf_documents in mongo_data.items():
        for document in pdf_documents:
            documents_to_insert.append(document)

    # Insert the list of documents into the collection
    if documents_to_insert:
        collection_pdf.insert_many(documents_to_insert).inserted_ids
        logger.info(
            f"Successfully inserted {len(documents_to_insert)} documents into MongoDB"
        )
    else:
        logger.error("No documents to insert")


def load_url(pdf_title: str, pdf_url: str):
    """
    Load a URL into MongoDB.

    Args:
        pdf_title (str): Title of the PDF.
        pdf_url (str): URL of the PDF.

    Returns:
        None
    """
    document = {"title": pdf_title, "url": pdf_url}

    result = collection_url.insert_one(document)
    if result.inserted_id:
        logger.info(f"URL '{pdf_url}' with title '{pdf_title}' successfully inserted.")
    else:
        logger.error("Error during the insertion of the URl into MongoDB.")
