// src/pages/Home.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ASCIIText from '../Rc_Animation/text-animations/ASCIIText';
// import StarBorder from '../Rc_Animation/animations/StarBorder';
import PixelCard from '../Rc_Animation/components/PixelCard';
import '../styles/Home.css';

const Home = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // 檢查 localStorage 是否有 token
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleGoToMarket = () => {
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/stock-market');
    } else {
      navigate('/login');
    }
    
  };

  return (
    <div className="home-container">
      <div className="content-wrapper">
        <div className="ascii-wrapper">
          <ASCIIText
            as="h1"
            text="FTEFREAK"
            enableWaves={true}
            asciiFontSize={8}
            style={{ marginBottom: '3rem' }}
          />
        </div>
        <div className="button-wrapper">
          <PixelCard
            as="button"
            type = "submit"
            className="market-button"
            color="white"
            speed="3s"
            onClick={handleGoToMarket}
          >
            {isLoggedIn ? 'In' : 'Sign In / Sign Up'}
          </PixelCard>
        </div>
      </div>
    </div>
  );
};

export default Home;