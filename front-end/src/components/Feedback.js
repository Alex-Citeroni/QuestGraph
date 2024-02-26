import "https://cdn.lordicon.com/lordicon.js";
import { motion } from "framer-motion";
import React, { useState, useEffect, useRef } from 'react';
import { saveFormData } from './firebaseConfig';
import "../styles/feedback.css";
import toast from 'react-hot-toast';

// Componente Pop-Up
function PopupForm({ messages, like, onClose }) {
    const [errorMessage, setErrorMessage] = useState('');

    // Funzione per gestire il clic esterno
    function handleClickOutside(event) {
        if (modalRef.current && !modalRef.current.contains(event.target)) {
            onClose();
        }
    }

    useEffect(() => {
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    async function handleSubmit(event) {
        event.preventDefault();
        const comment = document.getElementById("comment").value;
        const suggestedAnswer = document.getElementById("answer").value;
        const texts = messages.map(message => message.text);

        // Crea un oggetto con i dati del form
        const formData = {
            feedback: like,
            comment,
            suggestedAnswer,
            userQuestion: texts[0],
            ragAnswer: texts[1]
        };

        toast.success(`Feedback saved successfully!`);

        try {
            await saveFormData(formData);
            onClose();
        } catch (error) {
            setErrorMessage('Errore nel salvataggio dei dati.');
        }
    }

    const modalRef = useRef();


    return (
        <div className="popup" ref={modalRef}>
            <div className="modal-header">
                <h2>Feedback</h2>
                <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                    <lord-icon
                        title="Close"
                        onClick={onClose}
                        src="https://cdn.lordicon.com/nqtddedc.json"
                        trigger="hover"
                        state="hover-cross-3"
                        style={{ width: "30px", height: "30px", cursor: "pointer" }}
                    />
                </motion.div>
            </div>
            <form onSubmit={handleSubmit}>
                <h3 htmlFor="comment">Write your comment</h3>
                <textarea id="comment" rows="3" placeholder="Type in your comment (optional)"></textarea>

                <h3 htmlFor="answer">Recommend an answer</h3>
                <textarea id="answer" rows="3" placeholder="Recommend an answer (optional)"></textarea>

                {errorMessage && <div className="error-message" aria-live="assertive">{errorMessage}</div>}
                <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className={"share"} onClick={handleSubmit} >
                    <button type="submit" style={{ background: 'none', border: 'none', cursor: "pointer" }}>
                        <lord-icon
                            src="https://cdn.lordicon.com/oqdmuxru.json"
                            trigger="morph"
                            state="morph-check-in-2"
                            style={{ width: "30px", height: "30px" }}
                            title="Send Feedback"
                        />
                    </button>
                </motion.div>
            </form>
        </div>
    );
};

export default PopupForm;