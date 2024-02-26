from Documents import Documents
import umap
import matplotlib.pyplot as plt
import matplotlib
from firebase_operations import upload_umap_to_firebase
import os
import re
import numpy as np

matplotlib.use("Agg")


# Funzione per eliminare il file locale
def delete_local_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} eliminato con successo.")
    else:
        print(f"Il file {file_path} non esiste.")


def create_umap_visualization(
    query: str, title_of_pdf: str, embedding_fit, ranked_documents
):
    # Get embeddings of all documents and the top retrieved documents
    top_docs_embeddings = [embedding_fit[id] for id in ranked_documents[:5]]

    # Converti top_docs_embeddings in un array NumPy
    top_docs_embeddings_array = np.array(top_docs_embeddings)

    # Crea il grafico
    plt.scatter(
        embedding_fit[:, 0],
        embedding_fit[:, 1],
        alpha=0.5,
        label="All Documents",
    )

    plt.scatter(
        top_docs_embeddings_array[:, 0],
        top_docs_embeddings_array[:, 1],
        color="red",
        edgecolor="black",
        label="Top Documents",
    )

    # Mark the answer's position (assuming the first retrieved document is the answer)
    answer_embedding_projected = embedding_fit[ranked_documents[0]]
    plt.scatter(
        answer_embedding_projected[0],
        answer_embedding_projected[1],
        color="green",
        marker="X",
        s=40,
        label="Answer",
    )

    title_query = query.replace(" ", "_")
    title_of_pdf = title_of_pdf.replace(" ", "_")

    title_of_pdf = re.sub(r"[^\w\s-]|[\?@#]", "", title_of_pdf)
    title_query = re.sub(r"[^\w\s-]|[\?@#]", "", title_query)

    file_name = title_of_pdf + "_umap_visualization_" + title_query + ".png"

    # Visualize the results
    plt.xlabel("UMAP Dimension 1")
    plt.ylabel("UMAP Dimension 2")
    plt.legend(loc="best")
    plt.title("UMAP Visualization")
    plt.grid(True)
    plt.savefig(file_name, bbox_inches="tight")
    plt.close()
    link = upload_umap_to_firebase(file_name)
    delete_local_file(file_name)
    return link


def create_initial_umap_visualization(json_url: str, title_of_pdf: str):
    # Carica i documenti
    docs = Documents(json_url)
    # Crea la mappa UMAP
    reducer = umap.UMAP()
    # Ottieni gli embedding dei documenti
    embedding = reducer.fit_transform(docs.docs_embs)

    title_of_pdf = title_of_pdf.replace(" ", "_")
    title_of_pdf = re.sub(r"[^\w\s-]|[\?@#]", "", title_of_pdf)
    file_name = title_of_pdf + "_umap_visualization.png"

    # Visualizza i risultati
    plt.scatter(embedding[:, 0], embedding[:, 1], label="All Documents")
    plt.xlabel("UMAP Dimension 1")
    plt.ylabel("UMAP Dimension 2")
    plt.legend(loc="best")
    plt.grid(True)
    plt.title("UMAP Visualization")
    plt.savefig(file_name, bbox_inches="tight")
    plt.close()
    link = upload_umap_to_firebase(file_name)
    delete_local_file(file_name)
    return link, embedding
