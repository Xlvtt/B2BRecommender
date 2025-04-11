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
        region = self.buyers["FINAL_PARENT_OKATO_NAME"][self.buyers["PERSON_ID"] == buyer_id].iloc[0]

        interactions = self.df_train[self.df_train["BUYER_PERSON_ID"] == buyer_id]
        lots = self.df_lot[self.df_lot["LOT_ID"].isin(interactions["LOT_ID"].unique())].reset_index()

        offers_count = interactions["IS_SELLER"].sum()
        unique_offers_count = interactions.groupby("OFFER_PERSON_ID")["IS_SELLER"].max().sum()

        max_start_price = lots["TOTAL_START_PRICE_RUBLES"].max()
        min_start_price = lots["TOTAL_START_PRICE_RUBLES"].min()

        offers = pd.merge(interactions["LOT_ID"], self.df_offer, on="LOT_ID", how="inner")
        max_end_price = offers["OFFERED_PRICE_RUBLES"].max()
        min_end_price = offers["OFFERED_PRICE_RUBLES"].min()

        try:
            favourite_seller = interactions["OFFER_PERSON_ID"].value_counts().index[0]
        except IndexError:
            favourite_seller = None

        return {
            "region": region,
            "unique_offers_count": unique_offers_count,
            "offers_count": offers_count,
            "lots_info": lots.head(5),
            "max_start_price": max_start_price,
            "min_start_price": min_start_price,
            "max_end_price": max_end_price,
            "min_end_price": min_end_price,
            "favourite_seller_info": favourite_seller
        }

    def get_seller_info(self, seller_id):
        region = self.df_person[self.df_person["PERSON_ID"] == seller_id].reset_index()["FINAL_PARENT_OKATO_NAME"].iloc[0]
        interactions = self.df_train[self.df_train["OFFER_PERSON_ID"] == seller_id]

        lots = self.df_lot[self.df_lot["LOT_ID"].isin(interactions["LOT_ID"].unique())].reset_index()

        total_wins = interactions["IS_SELLER"].sum()
        total_lots = len(interactions)
        win_rate = f"{round(100 * total_wins / total_lots, 2)}%"

        flags_list = ["CANCELLED_FLAG", "INCONSISTENT_FLAG", "UNCONSIDERED_FLAG", "REJECT_FLAG", "CUSTOMER_REFUSAL_FLAG"]
        offers = self.df_offer[self.df_offer.isin(lots["LOT_ID"])].reset_index()

        flags_rates = {flag: f"{round(100 * offers[flag].sum() / len(interactions), 2)}%" for flag in flags_list}

        result = {
            "region": region,
            "win_rate": win_rate,
            "total_wins": total_wins,
            "total_lots": total_lots,
            "lots_info": lots.head(5)
        }
        result.update(flags_rates)
        return result

        # TODO число шагов и дианмика цен
        # TODO инфо для новых заказчиков
