from tornadowebapi.deserializers import BasicRESTDeserializer
from tornadowebapi.parsers import JSONParser
from tornadowebapi.renderers import JSONRenderer
from tornadowebapi.serializers import BasicRESTSerializer
from .base_transport import BaseTransport


class BasicRESTTransport(BaseTransport):
    def __init__(self):
        self.parser = JSONParser()
        self.renderer = JSONRenderer()
        self.serializer = BasicRESTSerializer()
        self.deserializer = BasicRESTDeserializer()

    @property
    def content_type(self):
        return "application/json"
