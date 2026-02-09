import React, { useState } from "react";
import { getCodeExplanation } from "./services/api.service";
import Header from "./components/Header";
import CodeEditor from "./components/CodeEditor";
import ExplanationPanel from "./components/ExplanationPanel";

const App = () => {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("javascript");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExplain = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getCodeExplanation(code, language);
      setResult(data);
    } catch (err) {
      setError(
        err.response?.data?.message || "Failed to connect to AI service",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-[#020617] to-[#020617] text-slate-100">
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-8">
        <CodeEditor
          code={code}
          setCode={setCode}
          language={language}
          setLanguage={setLanguage}
          onAction={handleExplain}
          isLoading={loading}
        />

        <ExplanationPanel
          explanation={result?.explanation}
          isLoading={loading}
          error={error}
        />
      </main>
    </div>
  );
};

export default App;
