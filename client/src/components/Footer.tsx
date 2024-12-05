import React from "react";

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white text-center py-4">
      <p>&copy; 2024 MarketAI. All Rights Reserved.</p>
      <p>
        Contact us at <a href="mailto:support@marketai.com" className="underline">support@marketai.com</a>
      </p>
    </footer>
  );
};

export default Footer;
