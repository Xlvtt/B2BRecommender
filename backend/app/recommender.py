from data_loader import DataLoader


class Recommender:
    def __init__(self):
        self.data = DataLoader()

    def recommend(self, buyer_id):
        # Здесь ваша логика рекомендаций
        return [
            {
                "supplier_id": "SUPPLIER_001",
                "supplier_region": "Москва",
                "lots": [
                    {
                        "lot_id": "LOT_123",
                        "win_rate": 0.85,
                        "lot_name": "Закупка компьютеров",
                        "total_price": 1500000,
                        "products": [
                            {"name": "Ноутбук", "qnty": 50, "unit_price": 30000}
                        ]
                    }
                ]
            }
        ]