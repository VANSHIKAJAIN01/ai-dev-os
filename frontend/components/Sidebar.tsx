"use client";
// Sidebar.tsx — Left panel showing projects and navigation
// "use client" means this runs in the browser (not server-side)
// because it has interactive state (selected project)

import { useState } from "react";

const DEMO_PROJECTS = [
  { id: "project-1", name: "ai-dev-os", repo: "VANSHIKAJAIN01/ai-dev-os" },
];

export default function Sidebar() {
  const [selected, setSelected] = useState("project-1");

  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-lg font-bold text-white">AI Dev OS</h1>
        <p className="text-xs text-gray-400 mt-0.5">Developer AI Platform</p>
      </div>

      {/* Projects list */}
      <div className="flex-1 p-3 overflow-y-auto">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">
          Projects
        </p>
        {DEMO_PROJECTS.map((project) => (
          <button
            key={project.id}
            onClick={() => setSelected(project.id)}
            className={`w-full text-left px-3 py-2 rounded-lg mb-1 text-sm transition-colors ${
              selected === project.id
                ? "bg-blue-600 text-white"
                : "text-gray-300 hover:bg-gray-800"
            }`}
          >
            <div className="font-medium truncate">{project.name}</div>
            <div className="text-xs opacity-60 truncate">{project.repo}</div>
          </button>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <p className="text-xs text-gray-500">Phase 1 — RAG Chat</p>
      </div>
    </aside>
  );
}
