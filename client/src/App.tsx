import React from "react";
import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import StockDetailsPage from "./pages/StockDetailsPage";
import Navbar from "./components/Navbar";
import StockChartSidebar from "./components/sidebars/StockChartSidebar";
import DashboardSidebar from "./components/sidebars/DashboardSidebar";
import Footer from "./components/Footer";
import { AppProvider } from "./context/AppContext";

const SidebarSwitcher: React.FC = () => {
  const location = useLocation();

  // Determine the sidebar to render based on the current route
  if (location.pathname.startsWith("/stock")) {
    return <StockChartSidebar />;
  }

  // Default to the dashboard sidebar
  return <DashboardSidebar />;
};


const App: React.FC = () => {
  return (
    <AppProvider>
      <Router>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          <div className="flex flex-1">
            <SidebarSwitcher />
            <main className="flex-1 p-4 bg-gray-100">
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/stock/:symbol" element={<StockDetailsPage />} />
              </Routes>
            </main>
          </div>
          <Footer />
        </div>
      </Router>
    </AppProvider>
  );
};

export default App;
