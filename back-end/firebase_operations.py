from dotenv import load_dotenv
import os
import pyrebase

load_dotenv(verbose=True)

# Constants for API keys
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
AUTH_DOMAIN = os.getenv("AUTH_DOMAIN")
DATABASE_URL = os.getenv("DATABASE_URL")
PROJECT_ID = os.getenv("PROJECT_ID")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")
MESSAGING_SENDER_ID = os.getenv("MESSAGING_SENDER_ID")
APP_ID = os.getenv("APP_ID")
MEASUREMENT_ID = os.getenv("MEASUREMENT_ID")

# Config per Firebase
firebaseConfig = {
    "apiKey": FIREBASE_API_KEY,
    "authDomain": AUTH_DOMAIN,
    "databaseURL": DATABASE_URL,
    "projectId": PROJECT_ID,
    "storageBucket": STORAGE_BUCKET,
    "messagingSenderId": MESSAGING_SENDER_ID,
    "appId": APP_ID,
    "measurementId": MEASUREMENT_ID,
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)

# Retrieve configuration for Firebase Storage service
storage = firebase.storage()


def upload_umap_to_firebase(umap: str):
    # Percorso del file nell'archivio Firebase Storage
    path_on_cloud = "umap/" + umap

    # Upload the image file to Firebase Storage
    storage.child(path_on_cloud).put(umap)

    # Get the link for the newly uploaded file
    return storage.child(path_on_cloud).get_url(None)


def upload_images_to_firebase(pdf_name: str):
    """
    Upload images associated with a PDF document to Firebase Storage and return the URLs of the images.

    Args:
        pdf_name (str): The name of the PDF document (without extension) for which to upload images.

    Returns:
        dict: A dictionary containing image URLs for each page of the PDF.
    """

    # Get the list of image files in the specified path
    image_folder = f"{pdf_name}_images"
    image_files = [file for file in os.listdir(image_folder) if file.endswith((".png"))]

    # Dictionary to store image URLs for each page
    image_urls_dict = {}

    # Upload each image file to Firebase Storage
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)

        # Specify the destination path on Firebase Storage
        destination_path = f"images/{pdf_name}/{image_file}"

        # Upload the image file to Firebase Storage
        storage.child(destination_path).put(image_path)

        # Get the link for the newly uploaded file
        image_url = storage.child(destination_path).get_url(None)

        # Get the page number from the image file URL
        page_num = int(image_file.split("_")[1])

        # Add the URL to the list of URLs for the corresponding page
        if page_num not in image_urls_dict:
            image_urls_dict[page_num] = []
        image_urls_dict[page_num].append(image_url)

    # Return the dictionary of image URLs
    return image_urls_dict


def upload_json_to_firebase(file_name: str):
    """
    Upload a JSON file to Firebase Storage and return the URL of the newly uploaded file.

    Args:
        file_name (str): The name of the JSON file to upload.

    Returns:
        str: The URL of the JSON file on Firebase Storage.
    """

    # Get the absolute path of the JSON file
    file_path = os.path.abspath(file_name)

    # Specify the destination path on Firebase Storage
    destination_path = f"JSON/{file_name}"

    # Upload the JSON file to Firebase Storage
    storage.child(destination_path).put(file_path)

    # Get the link for the newly uploaded JSON file
    json_url = storage.child(destination_path).get_url(None)

    # Return the URL of the JSON file on Firebase
    return json_url
