from .base_serializer import BaseSerializer


class BasicRESTSerializer(BaseSerializer):
    """Serialize with our own style of REST content."""
    def serialize_items_response(self, items_response):

        return {"items": [
            str(item.identifier) for item in items_response.items
            ]}

    def serialize_exception(self, exception):
        data = {
            "type": exception.__name__
        }

        message = getattr(exception, "message")

        if message is not None:
            data["message"] = message

        info = getattr(exception, "info")
        if info is not None:
            data.update(info)

        return data

    def serialize_resource(self, resource):
        d = {}

        for trait_name, trait_class in resource.traits:
            d[trait_name] = getattr(resource, trait_name)

        return d
