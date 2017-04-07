from .base_serializer import BaseSerializer


class BasicRESTSerializer(BaseSerializer):
    """Serialize with our own style of REST content."""
    def serialize_collection(self, collection_name, collection_items):
        return {"items": [str(item) for item in collection_items]}

    def serialize_exception(self, exception_representation):
        return exception_representation

    def serialize_resource(self,
                           collection_name,
                           identifier,
                           resource_representation):
        return resource_representation
