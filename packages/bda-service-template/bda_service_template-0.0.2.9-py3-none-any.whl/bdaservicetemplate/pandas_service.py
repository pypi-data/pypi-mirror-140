from .spark_service import SparkService


class PandasService(SparkService):
    def __init__(self):
        super().__init__()

    def get_dataset(self):
        return super().get_dataset().toPandas()

    def save_dataset(self, dataset):
        super().save_dataset(self.spark.createDataFrame(dataset))
