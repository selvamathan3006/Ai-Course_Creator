/* File: static/css/style.css */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

body {
    font-family: 'Inter', sans-serif;
    background-color: #f0f2f5;
    color: #333;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
}

.container {
    background: #ffffff;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    width: 100%;
    max-width: 700px;
    text-align: center;
}

header h1 {
    font-size: 2.5rem;
    color: #1a237e;
    margin-bottom: 10px;
}

header p {
    font-size: 1.1rem;
    color: #555;
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 20px;
    text-align: left;
}

.form-group label {
    display: block;
    font-weight: 500;
    margin-bottom: 8px;
    color: #333;
}

input[type="text"], select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
}

/* Base style for both radio and checkbox groups */
.radio-group, .checkbox-group {
    display: flex;
    flex-wrap: wrap; /* Allow wrapping for many options */
    justify-content: flex-start;
    gap: 10px; /* Spacing between items */
    padding: 10px;
    background: #f7f7f7;
    border-radius: 8px;
}

.radio-group input[type="radio"], 
.checkbox-group input[type="checkbox"] {
    display: none;
}

.radio-group label,
.checkbox-group label {
    cursor: pointer;
    padding: 10px 15px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    transition: all 0.3s ease;
    white-space: nowrap; /* Prevent labels from breaking */
    margin: 0; /* Remove default margins */
}

/* Style for CHECKED Radio and Checkbox */
.radio-group input[type="radio"]:checked + label,
.checkbox-group input[type="checkbox"]:checked + label {
    background-color: #1a237e;
    color: white;
    border-color: #1a237e;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

button {
    width: 100%;
    padding: 15px;
    font-size: 1.2rem;
    font-weight: 700;
    color: white;
    background: linear-gradient(90deg, #3949ab, #1a237e);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.hidden {
    display: none !important;
}

#loading {
    margin-top: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.spinner {
    border: 6px solid #f3f3f3;
    border-top: 6px solid #1a237e;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

#results {
    margin-top: 30px;
    text-align: left;
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
}

/* --- NEW STYLES FOR RESULT MESSAGES --- */

.success-msg {
    color: #1e8449; /* Dark Green */
    background-color: #e6f7ee; /* Light Green Background */
    border: 1px solid #c8e6c9;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 6px;
    font-weight: 500;
}

.error-msg {
    color: #c0392b; /* Dark Red */
    background-color: #fcebeb; /* Light Red Background */
    border: 1px solid #e9b3b3;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 6px;
    font-weight: 500;
}

/* Ensure links in results are visible */
.success-msg a {
    color: #1a237e;
    text-decoration: underline;
}
/* Progress Section */
#progressContainer {
    margin-top: 20px;
    text-align: center;
}

#progressBar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 10px;
    height: 20px;
    overflow: hidden;
    margin: 10px 0;
}

#progressFill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #3949ab, #1a237e);
    border-radius: 10px;
    transition: width 0.5s ease-in-out;
}

/* Remaining time */
#remainingTime {
    font-size: 0.95rem;
    color: #555;
}

/* Hidden logs container */
#logsContainer {
    display: none;
    background-color: #f7f7f7;
    border: 1px solid #ccc;
    padding: 15px;
    margin-top: 10px;
    max-height: 200px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 14px;
    border-radius: 8px;
    white-space: pre-wrap; /* Keep formatting from logs */
}

/* Toggle button for logs */
#toggleLogsBtn {
    display: block;
    width: 100%;
    background-color: #3949ab;
    color: white;
    font-weight: 700;
    padding: 12px;
    border: none;
    border-radius: 8px;
    margin-top: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
}

#toggleLogsBtn:hover {
    background-color: #1a237e;
}

