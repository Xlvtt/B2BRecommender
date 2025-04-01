import os
from loader import DataLoader
from rectools.models import ImplicitALSWrapperModel
from rectools.dataset import Dataset
from rectools.columns import Columns
from implicit.als import AlternatingLeastSquares
from rectools.models import PopularModel


class Recommender:
    def __init__(self, data_loader: DataLoader):
        self.data = data_loader
        os.environ["OPENBLAS_NUM_THREADS"] = "1"
        base_model = AlternatingLeastSquares(
            factors=64,
            regularization=0.01,
            alpha=1.0,
            calculate_training_loss=True,
            iterations=5
        )

        self.train_data = self.data.df_train.rename(columns={
            "OFFER_PERSON_ID": Columns.Item,
            "BUYER_PERSON_ID": Columns.User,
            "IS_SELLER": Columns.Weight
        }).groupby([Columns.User, Columns.Item]).max().reset_index()
        self.train_data[Columns.Datetime] = -1

        self.model = ImplicitALSWrapperModel(base_model, verbose=1)
        self.model.fit(
            Dataset.construct(self.train_data)
        )

        self.cold_model = PopularModel(
            popularity="n_users",
            verbose=1
        )
        self.cold_model.fit(
            Dataset.construct(self.train_data)
        )

    def recommend(self, buyer_id, k=10):
        model = self.model
        if buyer_id not in self.train_data[Columns.User].unique():
            model = self.cold_model
        return model.recommend(
            users=[buyer_id],
            dataset=Dataset.construct(self.train_data),
            k=k,
            filter_viewed=True
        )[Columns.Item]
