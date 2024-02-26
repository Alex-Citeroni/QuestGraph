import React, { useState, useEffect, useRef } from 'react';
import '../styles/drop_down.css';
import { motion } from "framer-motion";

function Dropdown({ onOptionSelect, options }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        closeDropdown();
      }
    };

    if (isOpen) {
      document.addEventListener('click', handleOutsideClick);
    }

    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, [isOpen]);

  const openDropdown = () => setIsOpen(true);
  const closeDropdown = () => setIsOpen(false);

  const selectOption = (option) => {
    onOptionSelect(option);
    closeDropdown();
  };

  return (
    <div ref={dropdownRef} className={`dropdown ${isOpen ? 'open' : ''}`} onClick={isOpen ? closeDropdown : openDropdown} >
      <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} className={"sel-bottone"}>
        <lord-icon src="https://cdn.lordicon.com/rbbnmpcf.json" trigger="hover" style={{ width: "26px", height: "26px" }} title="Select PDF" />
        <p>Select PDF</p>
      </motion.div>
      <ul className={`dropdown-list ${isOpen ? 'open' : ''}`}>
        {/*<li onClick={() => selectOption("ALL PDF")}>ALL PDF</li>*/}
        {options.map((option, index) => (<li key={index} onClick={() => selectOption(option)}>{option.pdfTitleKey}</li>))}
      </ul>
    </div>
  );
}

export default Dropdown;