import React, { useState, useEffect } from 'react';
import './index.css';
import BuyerSelect from './components/BuyerSelect.js';
import RecommendationCard from './components/RecommendationCard.js';

function App() {
  const [buyers, setBuyers] = useState([]);
  const [selectedBuyer, setSelectedBuyer] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
     fetch('http://localhost:8000/buyers')
        .then(res => {
          if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
          return res.json();
        })
        .then(data => setBuyers(data))
        .catch(error => console.error("Fetch error:", error));
  }, []);

  const handleRecommendations = (buyerId) => {
    fetch(`http://localhost:8000/recommendations/${buyerId}`)
      .then(res => res.json())
      .then(data => setRecommendations(data));
  };

  return (
    <div className="app">
      <BuyerSelect
        buyers={buyers}
        onSelect={handleRecommendations}
      />
      <div className="recommendations">
        {recommendations.map((rec, idx) => (
          <RecommendationCard key={idx} data={rec} />
        ))}
      </div>
    </div>
  );
}

export default App;