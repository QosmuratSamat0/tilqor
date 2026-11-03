import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./shared/i18n";
import "./shared/ui/theme.css";
import { App } from "./app/App";

const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
}
