import React, { useState } from "react";

const Sidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div
      className={`sidebar ${
        isCollapsed ? "w-16" : "w-64"
      } bg-gray-900 text-white flex flex-col transition-all duration-300`}
    >
      <button
        className="p-4 text-center focus:outline-none"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? ">" : "<"}
      </button>

      {!isCollapsed && (
        <ul className="mt-4">
          <li className="p-2">Filters</li>
          {/* Add more sidebar items here */}
        </ul>
      )}
    </div>
  );
};

export default Sidebar;
