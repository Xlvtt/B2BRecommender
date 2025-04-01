import os
import pandas as pd
from pathlib import Path


class DataLoader:
    def __init__(self):
        data_path = Path(os.getenv("DATA_PATH"))
        self.df_person = pd.read_csv(data_path / 'd_person.csv')
        self.df_lot = pd.read_csv(data_path/'d_lot.csv')
        self.df_lot_prod = pd.read_csv(data_path / 'd_lot_prod.csv')
        self.df_offer = pd.read_csv(data_path / 'd_offer.csv')
        self.df_train = pd.read_csv(data_path / 'all_ids_train.csv')

        self._preprocess()

    def _preprocess(self):
        self.df_person["FINAL_PARENT_OKATO_NAME"] = self.df_person["FINAL_PARENT_OKATO_NAME"].fillna(value="-")

        wins = self.df_train.groupby(['OFFER_PERSON_ID', 'LOT_ID'])['IS_SELLER'].mean().reset_index()
        self.win_rates = wins.rename(columns={'IS_SELLER': 'WIN_RATE'})

    def get_buyers(self):
        # PERSON_ID, FINAL_PARENT_OKATO_NAME
        return pd.merge(self.df_train["BUYER_PERSON_ID"], self.df_person, left_on="BUYER_PERSON_ID", right_on="PERSON_ID").drop(
            ["BUYER_PERSON_ID"], axis=1).drop_duplicates(subset=["PERSON_ID"], keep="first").to_dict(orient="records")

    def add_buyer(self, buyer_id, region):
        raise NotImplementedError("Add buyer method")
