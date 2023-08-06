from .generic_service import GenericService
from bdaserviceutils import HttpHealthServer, get_kafka_binder_brokers, get_input_channel, get_output_channel

class StreamingService(GenericService):

    def __init__(self):
        super().__init__()
        HttpHealthServer.run_thread()
