from fileioutilities.file_io import FileIO
from bdaserviceutils import get_args


class GenericService():
    def __init__(self):
        super().__init__()
        self._args = get_args()

    def download_model(self, path):
        fileIO = FileIO(storage_type=self._args['dataStorageType-input-model'])
        fileIO.download(remote_path=get_args()['input-model'], local_path=path)

    def upload_model(self, path):
        fileIO = FileIO(storage_type=self._args['dataStorageType-output-model'])
        fileIO.upload(local_path=path, remote_path=self._args['output-model'])
