import { initializeApp } from 'firebase/app';
import { getFirestore, serverTimestamp, collection, addDoc } from 'firebase/firestore';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import toast from 'react-hot-toast';

const firebaseConfig = {
    apiKey: "AIzaSyCtnzQXKKD0B9dJo2AjFc_-sDMyULKQ0J8",
    authDomain: "test-38b54.firebaseapp.com",
    databaseURL: "https://test-38b54-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "test-38b54",
    storageBucket: "test-38b54.appspot.com",
    messagingSenderId: "1051467746407",
    appId: "1:1051467746407:web:11fc9ae4013178000158c2",
    measurementId: "G-7N1M24JW8P"
};

// Initialize Firebase
const app_firebase = initializeApp(firebaseConfig);
const storage = getStorage(app_firebase);
const firestore = getFirestore(app_firebase);

const handleFileChange = async (event) => {
    const file = event.target.files[0];

    if (!file)
        return console.error('Nessun file selezionato');

    // Check if the file has a .pdf extension
    if (!file.name.toLowerCase().endsWith('.pdf'))
        return toast.error('The file must have the extension .pdf');

    // Crea un riferimento allo storage di Firebase
    const storageRef = ref(storage, 'PDF/' + file.name);
    const toastLoading = toast.loading("Loading...");
    try {
        // Carica il file nell'archivio di Firebase
        const snapshot = await uploadBytes(storageRef, file);

        // Ottieni l'URL del file appena caricato
        const downloadURL = await getDownloadURL(snapshot.ref);

        // Invia i dati al server Flask
        await fetch('http://localhost:5002/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fileName: file.name, downloadURL: downloadURL, }),
        });
        toast.dismiss(toastLoading);
        // Mostra una notifica di successo
        toast.success('File uploaded successfully!\nIt will take a few minutes to wait before viewing the PDF here.');

    } catch (error) {
        toast.dismiss(toastLoading);
        // Mostra una notifica di errore
        toast.error('Error during file upload');
    }
};

const saveFormData = async (formData) => {
    try {
        // Aggiungi i dati al database Firestore
        await addDoc(collection(firestore, "responses"), {
            ...formData,
            timestamp: serverTimestamp()
        });
        console.log("Form inviato con successo");
    } catch (error) {
        console.error("Errore nel salvataggio dei dati: ", error);
        throw error;
    }
};

export { saveFormData, handleFileChange };