import React, { useState, useEffect } from 'react';
import "../styles/modal.css";
import { motion } from "framer-motion";

function ModalContent({ closeInfo, pdfName }) {
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const timeoutId = setTimeout(() => setIsOpen(true), 0.01);
        return () => clearTimeout(timeoutId);
    }, []);

    const closeModal = () => {
        setIsOpen(false);
        setTimeout(() => closeInfo(), 500);
    };

    return (
        <div className={`modal-overlay ${isOpen ? 'open' : ''}`} onClick={closeModal}>
            <div className={`modal ${isOpen ? 'open' : ''}`} onClick={(event) => event.stopPropagation()}>
                <div className="modal-header">
                    <h2 className='titoli'>
                        <lord-icon
                            src="https://cdn.lordicon.com/axteoudt.json"
                            state="hover-help-center-2"
                            trigger="hover"
                            title="User Guide"
                            style={{ width: "30px", height: "30px" }}
                        />
                        User Guide for the Application
                    </h2>
                    <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                        <lord-icon
                            title="Close"
                            onClick={closeModal}
                            src="https://cdn.lordicon.com/nqtddedc.json"
                            trigger="hover"
                            state="hover-cross-3"
                            style={{ width: "40px", height: "40px", cursor: "pointer" }}
                        />
                    </motion.div>
                </div>
                <div className="modal-content">
                    <p>
                        This application allows you to upload a PDF file with an index and explore its structure through a Knowledge Graph. <br />
                        By interacting with the Knowledge Graph, you can read the content of the PDF and obtain detailed information for each paragraph, including:
                        <ul>
                            <li>Associated Knowledge Graph</li>
                            <li>Page Number</li>
                            <li>Paragraph Chapter</li>
                            <li>Paragraph Title</li>
                        </ul>
                        Additionally, you can interact directly with the PDF by asking questions about related topics and receiving answers, accompanied by the references used within the document. <br />
                        The app also offers a feedback feature, allowing you to submit your impressions and suggestions to enhance the user experience and the accuracy of the provided answers.
                    </p>

                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon src="https://cdn.lordicon.com/smwmetfi.json" trigger="hover" title="Upload the PDF" style={{ width: "26px", height: "26px" }} />
                            Uploading a PDF File
                        </h3>
                        <p>
                            Allows you to upload a PDF file to the application to interact with it, view the Knowledge Graph, read its content, and ask questions related to the PDF file. <br />
                            Currently, only PDF files in English are supported, and once uploaded, it is not possible to remove the PDF file.
                        </p>
                        <ol>
                            <li>Click on "Upload a PDF".</li>
                            <li>Select a PDF file from your PC.</li>
                            <li>Click on "Open".</li>
                            <li>Wait for the PDF file to be uploaded (a few seconds).</li>
                            <li>After uploading, wait approximately ten minutes for the processing of graphs and blocks.</li>
                            <li>Find the PDF file among the options in "Select a PDF".</li>
                        </ol>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon src="https://cdn.lordicon.com/rbbnmpcf.json" trigger="hover" style={{ width: "26px", height: "26px" }} title="Select PDF" />
                            Select a PDF File
                        </h3>
                        <p>Allows you to choose which PDF to view and ask questions about.</p>
                        <ol>
                            <li>Click on "Select a PDF".</li>
                            <li>Choose the desired PDF from the available options.</li>
                        </ol>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'><lord-icon src="https://cdn.lordicon.com/wpyrrmcq.json" trigger="morph" state="morph-trash-full" title="Clear" style={{ width: "26px", height: "26px" }} />
                            Clean All
                        </h3>
                        <p>Allows you to remove all previously clicked blocks and nodes.</p>
                        <ol>
                            <li>Click on "Clean All".</li>
                        </ol>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon src="https://cdn.lordicon.com/kkvxgpti.json" trigger="hover" title="Search" style={{ width: "30px", height: "30px" }} />
                            Search
                        </h3>
                        <p>Allows you to inquire about information regarding the PDF document and receive a coherent answer to the question, along with viewing the reference text from which the answer was derived.</p>
                        <ol>
                            <li>Write a question in the search bar.</li>
                            <li>Press enter or click on the magnifying glass.</li>
                            <li>View the answer in the lower box along with the reference text after a few seconds.</li>
                        </ol>

                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon
                                src="https://cdn.lordicon.com/zyzoecaw.json"
                                trigger="morph"
                                state="morph-book"
                                style={{ width: "26px", height: "26px" }}
                            />
                            PDF: {pdfName}
                        </h3>
                        <p>Allows you to view the hierarchical structure of the PDF.</p>
                        <ol>
                            <li>Click on "PDF: {pdfName}".</li>
                        </ol>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon
                                src="https://cdn.lordicon.com/whrxobsb.json"
                                trigger="hover"
                                style={{ width: "26px", height: "26px" }}
                            />
                            PDF UMAP
                        </h3>
                        <p>
                            Allows you to view the UMAP of RAG, where UMAP is a dimensionality reduction technique for visualizing high-dimensional data, standing for Uniform Manifold Approximation and Projection. <br />
                            RAG is an artificial intelligence model that combines search and text generation systems, with the acronym standing for Retrieval-Augmented Generation. <br />
                            Here, you can visualize within a vector space where questions are placed and which answers are retrieved.
                        </p>
                        <ol>
                            <li>Click on "PDF Overwiew".</li>
                        </ol>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon
                                src="https://cdn.lordicon.com/vdjwmfqs.json"
                                trigger="hover"
                                style={{ width: "26px", height: "26px" }}
                            />
                            PDF Knowledge Graph
                        </h3>
                        <p>
                            In the graph on the left side of the screen, the selected PDF file is represented, divided into nodes for chapters and paragraphs, and it can be interacted with in various ways.
                        </p>
                        <ul>
                            <li>Move: Use the mouse to navigate the interface.</li>
                            <li>Node Click: Click on a node to display its content in the side panels.</li>
                            <li>Zoom: Use the "+" and "-" buttons or the mouse scroll wheel to zoom in and out.</li>
                            <li>Return to Center: Click on the icon at the bottom left to center the graph.</li>
                            <li>Mini-map: Use the mini-map to navigate or see the current position in the graph.</li>
                        </ul>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon
                                src="https://cdn.lordicon.com/prjooket.json"
                                trigger="hover"
                                style={{ width: "26px", height: "26px" }}
                            />
                            Reference Paragraphs
                        </h3>
                        <p>
                            Blocks can contain both text and images.
                            In the case of text, there is also a Knowledge Graph that displays a graph based on the text block.
                        </p>
                        <ul>
                            <li>Images: Display the image with the "Close" button to close the block.</li>
                            <li>Text: Show the text and provide three buttons.
                                <ul>
                                    <li>"Original": Display the original text.</li>
                                    <li>"Info": Show chapter, paragraph, and page of the PDF.</li>
                                    <li>"Close": Close the block.</li>
                                </ul>
                            </li>
                            <li>Knowledge Graph: Graph with nodes and edges related to the text of the block, with operations similar to the PDF Knowledge Graph.</li>
                        </ul>
                    </div>
                    <div className='modal-content-paragraph'>
                        <h3 className='titoli'>
                            <lord-icon
                                src={"https://cdn.lordicon.com/dwoxxgps.json"}
                                trigger="hover"
                                state="hover-arrow-up-2"
                                style={{ width: "26px", height: "26px" }}
                                title="Up"
                            />
                            Feedback
                        </h3>
                        <p>
                            You can provide feedback on the chatbot's response by clicking 'like' if you found it helpful or 'dislike' if it didn't meet your expectations. <br />
                            Additionally, if you were not satisfied with the response, you have the option to comment on it and suggest a better answer. <br />
                            This feature enables continuous improvement of the chatbot's performance based on user input.
                        </p>
                        <ul>
                            <li>Click like or dislike on system answer.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ModalContent;
