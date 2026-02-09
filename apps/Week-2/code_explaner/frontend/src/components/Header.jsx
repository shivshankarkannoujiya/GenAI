import React from "react";

const Header = () => {
  return (
    <header className="bg-linear-to-r from-slate-900 to-slate-950 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-white tracking-tight">
          AI Code Explainer
        </h1>

        <span className="text-sm text-slate-400">Explain code using AI</span>
      </div>
    </header>
  );
};

export default Header;
