import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import LectureHelper from "./components/lecture-helper"; // Import your component

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <LectureHelper />
  </React.StrictMode>
);
