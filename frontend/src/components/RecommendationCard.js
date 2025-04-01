import React, { useState } from 'react';
import { motion } from 'framer-motion';

const RecommendationCard = ({ data }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      className="recommendation-card"
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="card-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>Поставщик: {data.supplier_id}</h3>
        <span>📍 {data.supplier_region}</span>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          className="arrow"
        >
          ▼
        </motion.div>
      </div>

      {isExpanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="lot-details"
        >
          {data.lots.map((lot, index) => (
            <div key={index} className="lot-item">
              <h4>{lot.lot_name}</h4>
              <p>🏷 Стартовая цена: {lot.total_price.toLocaleString()} ₽</p>
              <p>📈 Процент побед: {(lot.win_rate * 100).toFixed(1)}%</p>

              <div className="products-list">
                {lot.products.map((product, idx) => (
                  <div key={idx} className="product-item">
                    <span>{product.name}</span>
                    <div>
                      <span>{product.qnty} шт.</span>
                      <span>{product.unit_price.toLocaleString()} ₽/ед</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
};

export default RecommendationCard;