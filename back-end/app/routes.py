from app import app
from flask import request, jsonify
from PDFResearch import elabora_dati
from Documents import Documents
from Chatbot import Chatbot
from mongo_db_operations import collection_pdf, collection_url
from graph import process_document, sort_and_merge_nodes_and_edges
from umap_visualization import (
    create_umap_visualization,
    create_initial_umap_visualization,
)
import re

# Document structure
structure = {}

# Blocks
members = {}

# URLs
urls = {}

# PDF title
title_of_pdf = ""

# Links
links = {}

# Embeddings
embedding = []


# Chatbot
def run_chatbot(url):
    """
    Create an instance of the Documents class with the provided JSON file
    and an instance of the Chatbot class with the Documents instance.
    """
    documents = Documents(url)
    pdf_chatbot = Chatbot(documents)
    link, embedding_fit = create_initial_umap_visualization(url, title_of_pdf)
    embedding.clear()
    embedding.append(embedding_fit)
    links["PDF"] = link
    return pdf_chatbot


# Iterate over PDFs
for doc in collection_pdf.find():
    process_document(doc, structure, members)

# Iterate over URLs
for doc in collection_url.find():
    title = doc["title"]
    url = doc["url"]
    urls[title] = url
    title_of_pdf = title

# Iterate over PDF titles
for pdf_title, pdf_data in structure.items():
    sort_and_merge_nodes_and_edges(pdf_data)

    # Get the URL of the PDF
    pdf = urls.get(pdf_title, None)

    # Chatbot
    if pdf is not None:
        pdf_chatbot = run_chatbot(pdf)
    else:
        # Handle the case where the PDF URL is not found
        print(f"PDF URL not found for title: {pdf_title}")


# Routes
@app.route("/hierarchy")
def get_structure():
    return structure


@app.route("/members")
def get_data():
    return members


@app.route("/send-message", methods=["POST"])
def receive_message():
    data = request.get_json()
    user_message = data.get("message", "")

    # Execute the chatbot logic
    response = pdf_chatbot.generate_response(user_message)

    # Extract text from the response and send it to the frontend
    chatbot_response = ""
    for event in response:
        if event.event_type == "text-generation":
            chatbot_response += event.text

    ranked_documents = pdf_chatbot.get_ranked_docs()

    if ranked_documents:
        # Crea una visualizzazione UMAP per la query corrente
        links["Query"] = create_umap_visualization(
            user_message, title_of_pdf, embedding[0], ranked_documents
        )

        retrieved_docs = pdf_chatbot.get_doc_info()

        return jsonify(
            {"response": chatbot_response, "retrieved_docs": list(retrieved_docs)}
        )
    else:
        return jsonify({"response": chatbot_response, "retrieved_docs": []})


@app.route("/upload", methods=["POST"])
def handle_upload():
    data = request.get_json()

    file_name = data.get("fileName")
    download_url = data.get("downloadURL")

    # Remove or replace special characters (/, \, |, *, :, ?, <, >, ")
    file_name = re.sub(r'[\/\\|*:?<>"]', "", file_name)

    # Call the function in the other file
    elabora_dati(file_name, download_url)

    return jsonify(success=True)


@app.route("/url")
def get_urls():
    return urls


@app.route("/links")
def get_links():
    return links


@app.route("/url", methods=["POST"])
def set_urls():
    global pdf_chatbot
    data = request.get_json()
    # Run the chatbot
    if "url" in data:
        pdf_chatbot = run_chatbot(data["url"])
    return urls
