import React, { useState } from 'react';
import { motion } from 'framer-motion';

const BuyerSelect = ({ buyers, onSelect }) => {
  const [newRegion, setNewRegion] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const handleCreate = async () => {
    const response = await fetch('http://localhost:8000/buyers', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ region: newRegion }),
    });
    const data = await response.json();
    onSelect(data.id);
    setShowCreate(false);
  };

  return (
    <motion.div
      className="buyer-select"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="select-group">
        <select
          onChange={(e) => onSelect(e.target.value)}
          className="styled-select"
        >
          <option value="">Выберите заказчика</option>
          {buyers.map(buyer => (
            <option key={buyer.PERSON_ID} value={buyer.PERSON_ID}>
              {buyer.PERSON_ID} ({buyer.FINAL_PARENT_OKATO_NAME})
            </option>
          ))}
        </select>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="create-btn"
          onClick={() => setShowCreate(!showCreate)}
        >
          + Новый
        </motion.button>
      </div>

      {showCreate && (
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="create-form"
        >
          <input
            type="text"
            placeholder="Введите регион"
            value={newRegion}
            onChange={(e) => setNewRegion(e.target.value)}
          />
          <button onClick={handleCreate}>Создать</button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default BuyerSelect;