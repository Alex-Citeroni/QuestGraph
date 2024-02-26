import cohere
import hnswlib
import json
from typing import List, Dict
from io import StringIO
import requests

from dotenv import load_dotenv
import os

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))


class Documents:
    """
    A class representing a collection of documents.

    Parameters:
    sources (list): A list of dictionaries representing the sources of the documents. Each dictionary should have 'title' and 'url' keys.

    Attributes:
    sources (list): A list of dictionaries representing the sources of the documents.
    docs (list): A list of dictionaries representing the documents, with 'title', 'content', and 'url' keys.
    docs_embs (list): A list of the associated embeddings for the documents.
    retrieve_top_k (int): The number of documents to retrieve during search.
    rerank_top_k (int): The number of documents to rerank after retrieval.
    docs_len (int): The number of documents in the collection.
    index (hnswlib.Index): The index used for document retrieval.

    Methods:
    load(): Loads the data from the sources and partitions the HTML content into chunks.
    embed(): Embeds the documents using the Cohere API.
    index(): Indexes the documents for efficient retrieval.
    retrieve(query): Retrieves documents based on the given query.
    """

    def __init__(self, json_url: str):
        self.sources = []
        self.docs = []
        self.docs_embs = []
        self.retrieve_top_k = 10
        self.rerank_top_k = 3
        self.load_from_url(json_url)
        self.embed()
        self.index()

    def load_from_url(self, json_url: str) -> None:
        """
        Loads the documents from a JSON file URL and extracts titles and texts.

        Parameters:
        json_url (str): The URL of the JSON file containing document information.
        """
        print("Loading documents from JSON URL...")

        response = requests.get(json_url)
        if response.status_code == 200:
            data = json.load(StringIO(response.text))

        for chapter_key, chapters in data.items():
            for chapter, blocks in chapters.items():
                if chapter != "index":
                    for block_key, block_info in blocks.items():
                        for page_key, page_info in block_info.items():
                            if page_key != "images":
                                for a, b in page_info.items():
                                    if a == "title":
                                        title = b
                                    if a == "text":
                                        text = b

                                self.docs.append(
                                    {
                                        "title": title,
                                        "text": text,
                                        "info": block_key[block_key.find("_") + 1 :]
                                        + "_"
                                        + page_key[page_key.find(" ") + 1 :],
                                    }
                                )

    def embed(self) -> None:
        """
        Embeds the documents using the Cohere API.
        """
        print("Embedding documents...")

        batch_size = 90
        self.docs_len = len(self.docs)

        for i in range(0, self.docs_len, batch_size):
            batch = self.docs[i : min(i + batch_size, self.docs_len)]
            texts = [item["text"] for item in batch]
            docs_embs_batch = co.embed(
                texts=texts, model="embed-english-v3.0", input_type="search_document"
            ).embeddings
            self.docs_embs.extend(docs_embs_batch)

    def index(self) -> None:
        """
        Indexes the documents for efficient retrieval.
        """
        print("Indexing documents...")

        self.idx = hnswlib.Index(space="ip", dim=1024)
        self.idx.init_index(max_elements=self.docs_len, ef_construction=512, M=64)
        self.idx.add_items(self.docs_embs, list(range(len(self.docs_embs))))

        print(f"Indexing complete with {self.idx.get_current_count()} documents.")

    def retrieve(self, query: str) -> List[Dict[str, str]]:
        """
        Retrieves documents based on the given query.

        Parameters:
        query (str): The query to retrieve documents for.

        Returns:
        List[Dict[str, str]]: A list of dictionaries representing the retrieved documents, with 'title', 'text', and 'url' keys.
        """
        docs_retrieved = []
        query_emb = co.embed(
            texts=[query], model="embed-english-v3.0", input_type="search_query"
        ).embeddings

        doc_ids = self.idx.knn_query(query_emb, k=self.retrieve_top_k)[0][0]

        docs_to_rerank = []
        for doc_id in doc_ids:
            docs_to_rerank.append(self.docs[doc_id]["text"])

        rerank_results = co.rerank(
            query=query,
            documents=docs_to_rerank,
            top_n=self.rerank_top_k,
            model="rerank-english-v2.0",
        )

        doc_ids_reranked = []
        for result in rerank_results:
            doc_ids_reranked.append(doc_ids[result.index])

        for doc_id in doc_ids_reranked:
            docs_retrieved.append(
                {
                    "title": self.docs[doc_id]["title"],
                    "text": self.docs[doc_id]["text"],
                    "info": self.docs[doc_id]["info"],
                }
            )

        return docs_retrieved, doc_ids_reranked
