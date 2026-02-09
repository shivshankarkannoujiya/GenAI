import React from "react";

const CodeEditor = ({
  code,
  setCode,
  language,
  setLanguage,
  onAction,
  isLoading,
}) => {
  return (
    <div className="bg-linear-to-b from-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold tracking-widest text-slate-400">
          SOURCE CODE
        </h2>

        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="bg-slate-800 text-slate-200 text-sm px-3 py-1.5 rounded-lg border border-slate-700 outline-none"
        >
          <option value="javascript">JavaScript</option>
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
        </select>
      </div>

      {/* Editor */}
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Paste your function here..."
        className="w-full h-105 bg-transparent text-slate-100 placeholder:text-slate-500 resize-none outline-none font-mono text-sm leading-relaxed"
      />

      {/* Button */}
      <div className="flex justify-end mt-6">
        <button
          onClick={onAction}
          disabled={isLoading}
          className="bg-linear-to-r from-indigo-500 to-purple-500 
          hover:from-indigo-400 hover:to-purple-400
          disabled:opacity-50 disabled:cursor-not-allowed
          text-white font-semibold rounded-xl px-6 py-3
          shadow-lg shadow-indigo-500/20 transition"
        >
          {isLoading ? "Explaining..." : "Explain Concept"}
        </button>
      </div>
    </div>
  );
};

export default CodeEditor;
