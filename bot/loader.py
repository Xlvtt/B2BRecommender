import pandas as pd
from pathlib import Path


class DataLoader:
    def __init__(self, data_path: Path):
        try:
            self.df_person = pd.read_csv(data_path / 'd_person.csv')
            self.df_lot = pd.read_csv(data_path/'d_lot.csv')
            self.df_lot_prod = pd.read_csv(data_path / 'd_lot_prod.csv')
            self.df_offer = pd.read_csv(data_path / 'd_offer.csv')
            self.df_train = pd.read_csv(data_path / 'all_ids_train.csv')

            self._preprocess()
        except FileNotFoundError as e:
            print(f"Error loading data: {str(e)}")

    def _preprocess(self):
        self.df_person["FINAL_PARENT_OKATO_NAME"] = self.df_person["FINAL_PARENT_OKATO_NAME"].fillna(value="-")

        wins = self.df_train.groupby(['OFFER_PERSON_ID', 'LOT_ID'])['IS_SELLER'].mean().reset_index()
        self.win_rates = wins.rename(columns={'IS_SELLER': 'WIN_RATE'})

        self.buyers = self._get_buyers()

        self.regions = self.buyers["FINAL_PARENT_OKATO_NAME"].value_counts()

    def _get_buyers(self):
        # PERSON_ID, FINAL_PARENT_OKATO_NAME
        return pd.merge(self.df_train["BUYER_PERSON_ID"], self.df_person, left_on="BUYER_PERSON_ID", right_on="PERSON_ID").drop(
            ["BUYER_PERSON_ID"], axis=1).drop_duplicates(subset=["PERSON_ID"], keep="first")

    def add_buyer(self, buyer_id, region):
        self.buyers.loc[len(self.buyers)] = [buyer_id, region]
        self.df_person.loc[len(self.df_person)] = [buyer_id, region]

    def get_buyer_info(self, buyer_id):
        pass

    def get_seller_info(self, seller_id):
        pass

