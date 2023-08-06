import pandas as pd
from sklearn import svm

from energinetml import Model, TrainedModel, main


class NewModel(Model):
    def train(self, datasets, logger, **params):
        dataset = datasets["smoketest-dataset"]
        file_path = dataset.path("smoke_test_dataset.csv")

        df = pd.read_csv(file_path)

        clf = svm.SVC(gamma=0.001, C=100.0)
        clf.fit(df["age"].values.reshape(-1, 1), df["answer"].values)

        return TrainedModel(model=clf, features=["age"])

    def predict(self, trained_model, input_data, identifier):
        return trained_model.model.predict(input_data.as_pandas_dataframe())


# Reference your model class and name it "model"
model = NewModel

# Allow to invoke the CLI by executing this file (do not remove these lines)
if __name__ == "__main__":
    main()
