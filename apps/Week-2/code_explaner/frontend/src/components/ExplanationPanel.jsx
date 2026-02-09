import React from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

const ExplanationPanel = ({ explanation, isLoading, error }) => {
  return (
    <div className="bg-linear-to-b from-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <h2 className="text-sm font-semibold tracking-widest text-slate-400 mb-4">
        AI INSIGHTS
      </h2>

      {/* ERROR */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
          {error}
        </div>
      )}

      {/* LOADING */}
      {isLoading && !explanation && (
        <div className="flex items-center justify-center h-105 text-slate-500">
          AI is thinking...
        </div>
      )}

      {/* EMPTY */}
      {!isLoading && !explanation && !error && (
        <div className="flex items-center justify-center h-105 border border-dashed border-slate-700 rounded-xl text-slate-500">
          Enter code to see the magic ✨
        </div>
      )}

      {/* RESULT */}
      {!isLoading && explanation && (
        <div
          className="
            h-105 overflow-y-auto 
            prose prose-invert max-w-none
            prose-headings:text-slate-100
            prose-p:text-slate-300
            prose-strong:text-slate-100
            prose-code:text-indigo-300
            prose-pre:bg-slate-900
            prose-pre:border prose-pre:border-slate-800
            prose-pre:rounded-xl
          "
        >
          <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
            {explanation}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};

export default ExplanationPanel;
