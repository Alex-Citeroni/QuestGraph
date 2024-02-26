import fitz
import torch
import numpy as np
from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained("bert-large-cased")
model = BertModel.from_pretrained("bert-large-cased")


def find_top_similarities(pdf_path: str, keywords: list, top_k=5, threshold=0.2):
    """
    Find pages in a PDF document that are most similar to the provided keywords.

    Args:
        pdf_path (str): Path of the PDF document.
        keywords (list): List of keywords.
        top_k (int, optional): Maximum number of similar pages to return. Default: 5.
        threshold (float, optional): Similarity threshold. Pages with similarity above this threshold are considered. Default: 0.2.

    Returns:
        list: List of tuples (page number, similarity) for the top_k most similar pages.
    """
    # Assign weights to keywords
    keyword_weights = {
        "INDEX": 2.0,
        "TABLE OF CONTENTS": 1.5,
        "argument": 1.0,
        "CONTENTS": 1.5,
        "SUMMARY": 1.5,
        "LIST": 1.0,
        "FIGURES": 1.0,
    }

    with fitz.open(pdf_path) as doc:
        page_embeddings = []
        keyword_embeddings = []

        for page_number, page in enumerate(doc):
            page_text = page.get_text().upper()
            tokens = tokenizer(
                page_text, return_tensors="pt", truncation=True, padding=True
            )

            with torch.no_grad():
                outputs = model(**tokens)
                page_embedding = outputs.last_hidden_state.mean(dim=1).numpy()
                page_embeddings.append((page_number + 1, page_embedding))

        for keyword in keywords:
            keyword_upper = keyword.upper()
            keyword_tokens = tokenizer(
                keyword_upper, return_tensors="pt", truncation=True, padding=True
            )

            with torch.no_grad():
                keyword_outputs = model(**keyword_tokens)
                keyword_embedding = keyword_outputs.last_hidden_state.mean(
                    dim=1
                ).numpy() * keyword_weights.get(keyword_upper, 1.0)
                keyword_embeddings.append(keyword_embedding)

        # Calculate vector norms only once
        page_norms = [np.linalg.norm(page[1]) for page in page_embeddings]
        keyword_norms = [np.linalg.norm(keyword) for keyword in keyword_embeddings]

        similarities = []

        for keyword_index, keyword_embedding in enumerate(keyword_embeddings):
            for page_index, (page_number, page_embedding) in enumerate(page_embeddings):
                similarity = np.dot(page_embedding, keyword_embedding.T) / (
                    page_norms[page_index] * keyword_norms[keyword_index]
                )

                if similarity > threshold:
                    similarities.append((page_number, similarity))

        # Sort similarities in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return the top_k similarities
        top_similarities = similarities[:top_k]

        return top_similarities
