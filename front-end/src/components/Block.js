import React, { useState, useEffect } from 'react';
import BlockGraph from './BlockGraph';
import '../styles/block.css';
import { motion } from "framer-motion";

// Block component: Renders blocks of text and associated controls.
// Props:
// - nodeValue: Array of text values for each block.
// - nodeInfo: Array of node information objects.
// - nodeColor: Array of colors for each block.
// - onCloseBlock: Function to call when a block is closed.
export default function Block({ nodeValue, nodeInfo, nodeColor, onCloseBlock }) {
  const [selectedTextArray, setSelectedTextArray] = useState(new Array(nodeValue.length).fill(''));
  const [overlayVisible, setOverlayVisible] = useState(nodeValue.map(() => true));

  // Extract node ids from nodeInfo.
  const ids = nodeInfo.map(({ id }) => id);

  useEffect(() => {
    setOverlayVisible(nodeValue.map(() => true));
  }, [nodeValue]);

  // closeBlock: Closes a block and updates the parent component.
  // Input: index (Number) of the block, node (Object) information.
  // Output: Calls onCloseBlock with relevant data.
  const closeBlock = (index, node) => {
    if (nodeInfo[index].data.text)
      onCloseBlock(nodeInfo[index].data.text, nodeColor[index], nodeInfo[index]);
    else
      onCloseBlock(node, nodeColor[index], nodeInfo[index]);

    handleNodeClick(node, index)
  };

  // handleMenuClick: Handles click events on the menu, updating the block content.
  // Input: section (String), label (String), page (String), index (Number).
  // Output: Updates selectedTextArray with a formatted table of the content.
  const handleMenuClick = (section, label, page, index) => {
    const newSelectedTextArray = [...selectedTextArray];
    newSelectedTextArray[index] = (
      <table className="custom-table">
        <tbody>
          <tr className="table-row">
            <td className="static-word">Chapter:</td>
            <td className="dynamic-content">{section}</td>
          </tr>
          <tr className="table-row">
            <td className="static-word">Paragraph:</td>
            <td className="dynamic-content">{label}</td>
          </tr>
          <tr className="table-row">
            <td className="static-word">Page:</td>
            <td className="dynamic-content">{page}</td>
          </tr>
        </tbody>
      </table>
    );
    setSelectedTextArray(newSelectedTextArray);
  }

  // nodeTextGraph: Returns a JSX element representing the node text graph.
  // Input: node (Object) - the node information.
  // Output: JSX element.
  const nodeTextGraph = (node) => {
    return <div className='nodeTextGraph'>{node}</div>;
  }

  // handleNodeClick: Updates the selected text or content for a block.
  // Input: node (Object) - the node information, index (Number) - index of the block.
  // Output: Updates selectedTextArray.
  const handleNodeClick = (node, index) => {
    const newSelectedTextArray = [...selectedTextArray];
    newSelectedTextArray[index] = node;
    setSelectedTextArray(newSelectedTextArray);
  }

  // handleOverlayClick: Manages the visibility of the overlay.
  // Input: clickedIndex (Number) - the index of the clicked block.
  // Output: Updates overlayVisible to hide the overlay for the clicked block.
  const handleOverlayClick = (clickedIndex) => {
    const updatedOverlayVisible = overlayVisible.map((_, index) => index !== clickedIndex);
    setOverlayVisible(updatedOverlayVisible);
  };

  return (
    <div className='blocco'>
      {nodeValue.map((node, index) => {
        const isLink = node.startsWith('http://') || node.startsWith('https://');
        return (
          <div className='test' key={index}>
            <div className='blockTextContainer' style={{ backgroundColor: nodeColor[index], color: "white" }}>
              {isLink ? (
                <div className='immagine'>
                  <img className='img' src={node} alt="Page img" />
                  <button className='risposteMenu-item' onClick={() => closeBlock(index, node)}>Close</button>
                </div>
              ) : (
                <div>
                  <div className='risposteMenu'>
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className='img-button-1'
                      onClick={() => handleNodeClick(node, index)}
                    >
                      <lord-icon src="https://cdn.lordicon.com/eouimtlu.json" trigger="hover" style={{ width: "24px", height: "24px" }} />
                      <p>Original</p>
                    </motion.div>
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className='img-button-1'
                      onClick={() => handleMenuClick(nodeInfo[index].data.section, nodeInfo[index].data.label, nodeInfo[index].data.page, index)}
                    >
                      <lord-icon src="https://cdn.lordicon.com/yxczfiyc.json" trigger="hover" style={{ width: "24px", height: "24px" }} />
                      <p>Info</p>
                    </motion.div>
                    <span /><span /><span /><span />
                    <span className='separatore'>|</span>
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className='img-button-1'
                      onClick={() => closeBlock(index, node)}
                    >
                      <lord-icon src="https://cdn.lordicon.com/nqtddedc.json" trigger="hover" state="hover-cross-3" style={{ width: "24px", height: "24px" }} />
                      <p>Close</p>
                    </motion.div>
                  </div>
                  <div className='testi-grafo'>
                    <div className='separator' />
                    {selectedTextArray[index] || nodeTextGraph(node)}
                  </div>
                </div>
              )}
            </div>
            {!isLink && (
              <div className='grafoRisposte' style={{ border: `1px solid ${nodeColor[index]}`, position: 'relative' }}>
                {overlayVisible[index] && (
                  <div
                    className="overlay"
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      backgroundColor: 'rgba(255, 255, 255, 0.5)',
                      zIndex: 2 // Assicurati che l'overlay sia sopra il contenuto di grafoRisposte
                    }}
                    onClick={() => handleOverlayClick(index)}
                  />
                )}
                <BlockGraph block={ids[index]} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};