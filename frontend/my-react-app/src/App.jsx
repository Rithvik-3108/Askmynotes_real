import { useState } from "react";
import "./App1.css";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [uploadStatus, setUploadStatus] = useState("");
  const [status, setStatus] = useState("");

  // FastAPI backend
  // const BACKEND_URL = "http://127.0.0.1:8000";
  const BACKEND_URL = "https://askmynotes-real-backend.onrender.com";

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setUploadStatus("Please select a PDF file.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setUploadStatus("Uploading PDF...");
    setAnswer("");
    setSources([]);
    setStatus("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      console.log("Calling:", `${BACKEND_URL}/upload`);

      const response = await fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);

      const data = await response.json();

      console.log("Response data:", data);

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      setUploadStatus(
        `Uploaded successfully: ${data.filename}`
      );

    } catch (error) {
      console.error("UPLOAD ERROR:", error);

      setUploadStatus(
        `Failed to upload: ${error.message}`
      );

      setFile(null);
    }
  };

  const handleAsk = async () => {
    if (!file) {
      setStatus("Please upload a PDF first.");
      return;
    }

    if (!question.trim()) {
      setStatus("Please enter a question.");
      return;
    }

    setStatus("Getting answer...");
    setAnswer("");
    setSources([]);

    try {
      console.log("Calling:", `${BACKEND_URL}/ask`);

      const response = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      console.log("Ask status:", response.status);

      const data = await response.json();

      console.log("Ask data:", data);

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      setAnswer(data.answer || "No answer returned.");
      setSources(data.sources || []);
      setStatus("");

    } catch (error) {
      console.error("ASK ERROR:", error);

      setStatus(`Something went wrong: ${error.message}`);
    }
  };

  return (
    <div className="app">

      <div className="container">

        <div className="header">
          <h1>AskMyNotes</h1>

          <p>
            Upload your PDF and ask questions from your notes.
          </p>
        </div>

        <div className="section">

          <label className="section-label">
            Upload your notes
          </label>

          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={handleFileChange}
            className="file-input"
          />

          <p className="file-status">
            {uploadStatus || "No PDF selected."}
          </p>

        </div>

        <div className="section">

          <label
            htmlFor="question"
            className="section-label"
          >
            Ask a question
          </label>

          <textarea
            id="question"
            rows="4"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What do my notes say about..."
            className="question"
          />

          <div className="button-row">

            <p className="status">
              {status}
            </p>

            <button
              onClick={handleAsk}
              className="ask-button"
            >
              Ask
            </button>

          </div>

        </div>

        <div className="section">

          <h2 className="section-label">
            Answer
          </h2>

          <div className="answer-box">

            {answer ? (
              <p className="answer-text">
                {answer}
              </p>
            ) : (
              <p className="answer-placeholder">
                Your answer will appear here...
              </p>
            )}

          </div>

        </div>

        {sources.length > 0 && (
          <div className="sources">

            <h2>Sources</h2>

            <ol>
              {sources.map((source, index) => (
                <li key={index}>
                  {typeof source === "string"
                    ? source
                    : source.text || JSON.stringify(source)}
                </li>
              ))}
            </ol>

          </div>
        )}

      </div>

      <footer className="footer">
        AskMyNotes • AI-powered PDF Question Answering
      </footer>

    </div>
  );
}

export default App;