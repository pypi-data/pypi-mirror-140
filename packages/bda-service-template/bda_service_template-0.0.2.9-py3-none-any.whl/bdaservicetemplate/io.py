import os

class IO:
    @staticmethod
    def dataset_to_dataset(func):
        
        def wrapper(*args):
            self = args[0]
            dataset = self.get_dataset()
            resulting_dataset = func(self, dataset)
            self.save_dataset(resulting_dataset)

        return wrapper


    @staticmethod
    def dataset_to_model(func):
        
        def wrapper(*args):
            self = args[0]
            dataset = self.get_dataset()
            model_path = func(self, dataset)
            self.upload_model(model_path)

        return wrapper


    @staticmethod
    def dataset_and_model_to_dataset(func):
        
        def wrapper(*args):
            self = args[0]
            dataset = self.get_dataset()
            model_path = os.path.join(".", "model")
            self.download_model(path=model_path)
            resulting_dataset = func(self, dataset, model_path)
            self.save_dataset(resulting_dataset)

        return wrapper


    @staticmethod
    def dataset_and_model_to_dataset_and_model(func):
        
        def wrapper(*args):
            self = args[0]
            dataset = self.get_dataset()
            model_path = os.path.join(".", "model")
            self.download_model(path=model_path)
            resulting_dataset, resulting_model = func(self, dataset, model_path)
            self.save_dataset(resulting_dataset)
            self.upload_model(resulting_model)

        return wrapper

