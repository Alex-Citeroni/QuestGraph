import React, { useState, useRef, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PDFStructure from './components/PDFStructure';
import Block from './components/Block';
import Dropdown from './components/DropDown';
import "https://cdn.lordicon.com/lordicon.js";
import toast, { Toaster } from 'react-hot-toast';
import ModalContent from './components/ModalContent';
import './styles/App.css';
import { ReactFlowProvider } from 'reactflow';
import { motion } from "framer-motion";
import PopupForm from "./components/Feedback";
import { Umap } from './components/Umap';
import { saveFormData, handleFileChange } from './components/firebaseConfig';

function App() {
    const [selectedPDF, setSelectedPDF] = useState(null);
    const [textValues, setTextValues] = useState([]);
    const [options, setOptions] = useState([]);
    const [nodeColor, setNodeColor] = useState([]);
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [nodes, setNodes] = useState([]);
    const [nodeIdColorMap, setNodeIdColorMap] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const [nodesInfo, setNodesInfo] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const fileInputRef = useRef(null);
    const [selectedPDFVisible, setSelectedPDFVisible] = useState(false);
    const [isAnswerVisible, setIsAnswerVisible] = useState(false);
    const [collapse, setCollapse] = useState(new Set());
    const [showPopup, setShowPopup] = useState(false);
    const [like, setLike] = useState("");
    const [activeTab, setActiveTab] = useState('PDF');
    const [link, setLink] = useState("");
    const title = options.length > 0 ? options[0]["pdfTitleKey"] : "";
    const pdfStructureRef = useRef(null);

    // openInfo: Opens the modal.
    // Input: None
    // Output: Sets the state of isModalOpen to true.
    function openInfo() {
        return setIsModalOpen(true);
    }

    // closeInfo: Closes the modal.
    // Input: None
    // Output: Sets the state of isModalOpen to false.
    function closeInfo() {
        return setIsModalOpen(false);
    }

    // updateNodes: Updates the nodes state.
    // Input: Array of newNodes.
    // Output: Sets the new nodes in the state.
    function updateNodes(newNodes) {
        return setNodes(newNodes);
    }

    // handleRemoveAll: Resets the states associated with BlockText.
    // Input: None
    // Output: Resets multiple state variables to their initial state.
    function handleRemoveAll() {
        setTextValues([]);
        setNodeColor([]);
        setNodeIdColorMap({});
        setNodesInfo([]);
        setOptions([]);
        setMessages([]);
        setSelectedPDFVisible(false);
        setCollapse(new Set());
        setIsAnswerVisible(false);
        setLink("");
        setLike("");
        if (pdfStructureRef.current) pdfStructureRef.current.resetView();
    }

    // saveFeedback: Saves user feedback to the database.
    // Input: likeType (String) indicating the type of feedback ('like' or 'dislike').
    // Output: Saves the feedback data and shows a toast message.
    async function saveFeedback(likeType) {
        const texts = messages.map(message => message.text);

        // Crea un oggetto con i dati del feedback
        const formData = {
            feedback: likeType,
            userQuestion: texts[0],
            ragAnswer: texts[1]
        };

        try {
            await saveFormData(formData);
            toast.success(`Feedback '${likeType}' saved successfully!`);
        } catch (error) {
            toast.error('Errore nel salvataggio dei dati.');
            console.error('Error saving feedback:', error);
        }
    }

    const queryclient = new QueryClient();

    useEffect(() => {
        if (messages.length > 0)
            setIsAnswerVisible(true);

        setSelectedPDFVisible(nodesInfo.length !== 0);

    }, [messages, nodesInfo]);

    // handleOptionSelect: Handles the selection of an option in the dropdown.
    // Input: data (Object) containing the selected option.
    // Output: Makes a POST request with the selected data and updates the state.
    async function handleOptionSelect(data) {
        // Invia il messaggio al server Flask
        await fetch('http://localhost:5002/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: data.url }),
        });
        setSelectedPDF(data);
    }

    // closeAnswer: Closes the answer section.
    // Input: None
    // Output: Sets the isAnswerVisible state to false and closes the modal after a delay.
    function closeAnswer() {
        setIsAnswerVisible(false);
        setLike("");
        setTimeout(() => closeInfo(), 500);
    }

    // onNodeClick: Handles the click event on a node.
    // Input: nodeValue (String), nodeColor (String), node (Object)
    // Output: Updates the state based on the clicked node.
    function onNodeClick(nodeValue, nodeColor, node) {
        const index = textValues.indexOf(nodeValue);

        if (index === -1) {
            // Aggiungi i nuovi valori all'inizio dell'array
            setTextValues((prevTextValues) => [nodeValue, ...prevTextValues]);
            setNodesInfo((prevNodesInfo) => [node, ...prevNodesInfo]);
            setNodeColor((prevNodeColor) => [nodeColor, ...prevNodeColor]);
            setSelectedPDFVisible(true);
        } else {
            // Rimuovi il nodo esistente dagli array
            setTextValues((prevTextValues) => prevTextValues.filter((value, i) => i !== index));
            setNodesInfo((prevNodesInfo) => prevNodesInfo.filter((info, i) => i !== index));
            setNodeColor((prevNodeColor) => prevNodeColor.filter((color, i) => i !== index));

            if (textValues.length > 1) setSelectedPDFVisible(true);
            else setSelectedPDFVisible(false);
        }
    }

    // sendMessage: Sends the user's message to the server and processes the response.
    // Input: None (uses userInput state for the message content).
    // Output: Sends the message, updates the state with the response, and handles loading state.
    async function sendMessage() {
        setIsLoading(true);

        // Check if userInput is empty
        if (!userInput.trim()) {
            toast.error('Please enter a message');
            setMessages([{ role: 'user', text: 'Please enter a message' }]);
            setIsLoading(false);
            return;
        }
        const toastLoading = toast.loading("Loading...");
        return fetch('http://localhost:5002/send-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput }),
        }).then(async (response) => {
            toast.dismiss(toastLoading);
            const data = await response.json();

            setMessages([{ role: 'user', text: userInput }, { role: 'chatbot', text: data.response }]);
            setTextValues([]);
            setNodeColor([]);
            setNodesInfo([]);
            const newNodeIdColorMap = {};
            let initialAlpha = 1;

            nodes.forEach((node) => {
                data.retrieved_docs.forEach((new_node) => {
                    if (node.id === new_node) {
                        setTextValues((prevTextValues) => [...prevTextValues, node.data.text]);
                        setNodesInfo((prevNodesInfo) => [...prevNodesInfo, node]);
                        const chapter = node.data.section;
                        setCollapse((prevChapter) => new Set(prevChapter).add(chapter));
                        const color = `rgba(135, 206, 250, ${initialAlpha})`;
                        setNodeColor((prevNodeColor) => [...prevNodeColor, color]);
                        newNodeIdColorMap[new_node] = { backgroundColor: color, color: "#fff", edge: color, strokeWidth: 3 };
                        newNodeIdColorMap[chapter] = { backgroundColor: "rgb(135, 206, 250)", color: "#fff", edge: "rgb(135, 206, 250)", strokeWidth: 3 };
                        initialAlpha -= 0.25;
                    }
                });
            });

            // Chiamata GET a /links
            const linksResponse = await fetch('http://localhost:5002/links');
            if (!linksResponse.ok) {
                throw new Error('Failed to fetch links');
            }
            const linksData = await linksResponse.json();
            setLink(linksData);
            setLike("");
            setNodeIdColorMap(newNodeIdColorMap);
            setUserInput('');
            setIsLoading(false);
            toast.success('Got the data!');

            return 'Message sent successfully!';
        }).catch((error) => {
            console.error('Error during sendMessage:', error);
            toast.error('Error during message send');
            setIsLoading(false);
            return;
        });
    }

    // handleButtonClick: Handles the click event on the file input button.
    // Input: None
    // Output: Triggers the click event on the hidden file input.
    function handleButtonClick() { return fileInputRef.current.click(); }

    // closeBlock: Handles the closing of a block in the PDFStructure.
    // Input: nodeId (String) indicating which node to close.
    // Output: Updates the nodeIdColorMap state to reflect the closed node.
    function closeBlock(nodeId) {
        // Find the node in PDFStructure by nodeId and update its color to white
        setNodeIdColorMap((prevNodeIdColorMap) => {
            const newNodeIdColorMap = { ...prevNodeIdColorMap };
            newNodeIdColorMap[nodeId] = { backgroundColor: "#fff", color: "#000", edge: "rgba(177,177,183,255)", strokeWidth: 1.3 }; // Set the background color to white and text color to black
            return newNodeIdColorMap;
        });
    }

    // closePopup: Closes the feedback popup.
    // Input: None
    // Output: Sets the showPopup state to false.
    function closePopup() { setShowPopup(false); }

    // handleScroll: Prevents vertical scrolling and enables horizontal scrolling.
    // Input: e (Event) - the scroll event.
    // Output: Adjusts the current scroll position based on user's scroll action.
    const handleScroll = (e) => {
        // Impedisce lo scorrimento verticale
        e.preventDefault();
        // Accede direttamente all'elemento che ha scatenato l'evento e applica lo scorrimento orizzontale
        e.currentTarget.scrollLeft += e.deltaY;
    };

    return (
        <div className="App">
            <QueryClientProvider client={queryclient} >
                <Toaster position="top-right" reverseOrder={false} />
                <div className={`ContainerSearchBar ${!isAnswerVisible ? 'your-additional-class_answer' : ''} distanza `}>
                    <input type="file" onChange={handleFileChange} style={{ display: 'none' }} ref={fileInputRef} />
                    <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className={"sel-bottone btn-left1"} onClick={handleButtonClick}>
                        <lord-icon src="https://cdn.lordicon.com/smwmetfi.json" trigger="hover" title="Upload the PDF" style={{ width: "26px", height: "26px" }} />
                        <p>Upload PDF</p>
                    </motion.div>
                    <div className='btn-left2'>
                        <Dropdown onOptionSelect={handleOptionSelect} options={options} />
                    </div>
                    <div className='ContainerInputBottom'>
                        <motion.div whileHover={{ scale: 1.015 }} whileTap={{ scale: 1 }}>
                            <input
                                id="search_bar"
                                className='ImputSerach'
                                type="text"
                                value={userInput}
                                onChange={(e) => setUserInput(e.target.value)}
                                placeholder="Ask a question"
                                onKeyDown={async event => { if (event.code === "Enter") sendMessage() }}
                            />
                        </motion.div>
                        <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className={"inputBottom"} onClick={sendMessage}>
                            <lord-icon src="https://cdn.lordicon.com/kkvxgpti.json" trigger="hover" title="Search" style={{ width: "30px", height: "30px" }} />
                        </motion.div>
                    </div>
                    <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className={"sel-bottone btn-right1"} onClick={handleRemoveAll}>
                        <lord-icon src="https://cdn.lordicon.com/wpyrrmcq.json" trigger="morph" state="morph-trash-full" title="Clear" style={{ width: "26px", height: "26px" }} />
                        <p>Clean All</p>
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className={"sel-bottone btn-right2"} onClick={openInfo}>
                        <lord-icon src="https://cdn.lordicon.com/axteoudt.json" state="hover-help-center-2" trigger="hover" title="User Guide" style={{ width: "26px", height: "26px" }} />
                        <p>User Guide</p>
                    </motion.div>
                    {messages.length > 0 && (
                        <div className="answer">
                            {isLoading ?
                                <div className="loading">
                                    <lord-icon src="https://cdn.lordicon.com/lqxfrxad.json" trigger="loop" state="loop-queue" style={{ width: "100px", height: "100px" }} />
                                </div>
                                : messages.map((msg, index) => (
                                    <div key={index} className={`message ${msg.role}`}>
                                        <span className={msg.role === 'user' ? 'red-text pr' : 'hidden'} >
                                            <p className='pr1'>Your question: {msg.text}</p>
                                            <motion.div
                                                className='pr3'
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                                onClick={() => { setLike("like"); saveFeedback("like"); }}
                                            >
                                                <lord-icon
                                                    src={like !== 'like' ? "https://cdn.lordicon.com/dwoxxgps.json" : "https://cdn.lordicon.com/ternnbni.json"}
                                                    trigger="hover"
                                                    state="hover-arrow-up-2"
                                                    style={{ width: "23px", height: "23px" }}
                                                    title="Up"
                                                />
                                                <span>Like</span>
                                            </motion.div>
                                            <motion.div
                                                className='pr4'
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                                style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: "pointer" }}
                                                onClick={() => { setLike("dislike"); setShowPopup(true); }}
                                            >
                                                <lord-icon
                                                    src={like !== 'dislike' ? "https://cdn.lordicon.com/rmkahxvq.json" : "https://cdn.lordicon.com/xcrjfuzb.json"}
                                                    trigger="hover"
                                                    state="hover-arrow-down-2"
                                                    style={{ width: "23px", height: "23px" }}
                                                    title="Down"
                                                />
                                                <span>Dislike</span>
                                            </motion.div>
                                            <motion.div className='pr2' whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                                                <lord-icon
                                                    title="Close"
                                                    onClick={closeAnswer}
                                                    src="https://cdn.lordicon.com/nqtddedc.json"
                                                    trigger="hover"
                                                    state="hover-cross-3"
                                                    style={{ width: "25px", height: "25px", cursor: "pointer" }}
                                                />
                                            </motion.div>
                                        </span>
                                        <span className={msg.role === 'user' ? 'hidden' : 'black-text'}>{msg.text}</span>
                                    </div>
                                ))
                            }
                        </div>
                    )}
                    {showPopup && <>
                        <div className="overlay"></div>
                        <PopupForm messages={messages} like={like} onClose={closePopup} />
                    </>}
                </div>
                <div className={`blockTextAll ${!isAnswerVisible ? 'your-additional-class' : ''}`}>
                    <div className="firstFlow">
                        <motion.div
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className={`labelPDF left ${activeTab === 'PDF' ? 'tab-active' : ''}`}
                            onClick={() => setActiveTab('PDF')}
                            onWheel={handleScroll}
                        >
                            <div className='titolo'>
                                <lord-icon
                                    src="https://cdn.lordicon.com/zyzoecaw.json"
                                    trigger="morph"
                                    state="morph-book"
                                    style={{ width: "19px", height: "19px" }}
                                />
                                PDF: {title ? title : "NO"}
                            </div>
                        </motion.div>
                        <motion.div
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className={`labelPDF right ${activeTab === 'Overview' ? 'tab-active' : ''}`}
                            onClick={() => setActiveTab('Overview')}
                        >
                            <lord-icon
                                src="https://cdn.lordicon.com/whrxobsb.json"
                                trigger="hover"
                                style={{ width: "20px", height: "20px" }}
                            />
                            PDF UMAP
                        </motion.div>
                        <div className='structurePdf'>
                            <ReactFlowProvider>
                                <PDFStructure
                                    ref={pdfStructureRef}
                                    postDataPdf={selectedPDF}
                                    onNodeClick={onNodeClick}
                                    setOptions={setOptions}
                                    updateNodes={updateNodes}
                                    nodeIdColorMap={nodeIdColorMap}
                                    collapse={collapse}
                                />
                            </ReactFlowProvider>
                            <div className={`umap-overlay ${activeTab === 'Overview' ? 'show' : 'hide'}`}>
                                <Umap query={messages} link={link} />
                            </div>
                        </div>
                    </div>
                    <div className="blockText">
                        {selectedPDFVisible &&
                            <div className='structureBlock' >
                                <div style={{ backgroundColor: nodeColor[0] === "rgba(191, 230, 207,255)" ? "rgba(191, 230, 207, 255)" : 'rgb(135, 206, 250)' }}>
                                    <lord-icon
                                        src="https://cdn.lordicon.com/prjooket.json"
                                        trigger="hover"
                                        style={{ width: "20px", height: "20px" }}
                                    />
                                    Reference Paragraphs
                                </div>
                                <div style={{ backgroundColor: nodeColor[0] === "rgba(191, 230, 207,255)" ? "rgba(191, 230, 207, 255)" : 'rgb(135, 206, 250)' }}>
                                    <lord-icon
                                        src="https://cdn.lordicon.com/vdjwmfqs.json"
                                        trigger="hover"
                                        style={{ width: "20px", height: "20px" }}
                                    />
                                    Knowledge Graphs
                                </div>
                            </div>
                        }
                        <div className='structureBlockContainer'>
                            <Block
                                nodeValue={textValues}
                                nodeInfo={nodesInfo}
                                nodeColor={nodeColor}
                                onCloseBlock={(text, color, id, node) => { onNodeClick(text, color, node); closeBlock(id); }}
                            />
                        </div>
                    </div>
                </div>
                {isModalOpen && <ModalContent closeInfo={closeInfo} pdfName={title}></ModalContent>}
            </QueryClientProvider>
        </div>
    );
};

export default App;