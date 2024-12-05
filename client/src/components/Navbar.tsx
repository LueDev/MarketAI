// src/components/Navbar.tsx
import React from "react";
import { Link } from "react-router-dom";

const Navbar: React.FC = () => {
  return (
    <nav className="navbar bg-gray-900 text-white px-4 py-2">
      <h1 className="text-xl font-bold">
        <Link to="/">MarketAI</Link>
      </h1>
      <ul className="flex space-x-4">
        <li>
          <Link to="/" className="text-green-400">Dashboard</Link>
        </li>
        <li>
          <Link to="/about" className="text-white">About</Link>
        </li>
        <li>
          <Link to="/profile" className="text-white">Profile</Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
