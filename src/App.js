import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import StockMarket from './pages/StockMarket'; // 之後會建立這個頁面

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/stock-market" element={<StockMarket />} />
    </Routes>
  );
};

export default App;