from tornadowebapi.exceptions import WebAPIException
from tornadowebapi.traitlets import Absent, OneOf
from .base_serializer import BaseSerializer


class BasicRESTSerializer(BaseSerializer):
    """Serialize with our own style of REST content."""
    def serialize_items_response(self, items_response):
        # For security reasons stemming from cross site execution,
        # this list will not be rendered as a list in a json representation.
        # Instead, a dictionary with the key "items" and value as this list
        # will be returned.
        return {
            "offset": items_response.offset,
            "total": items_response.total,
            "items": {
                str(item.identifier): self.serialize_resource(item)
                for item in items_response.items
            }
        }

    def serialize_exception(self, exception):
        if not isinstance(exception, WebAPIException):
            raise TypeError("exception must be a "
                            "WebAPIException. Got {}".format(type(exception)))

        if exception.message is None and exception.info is None:
            return None

        data = {
            "type": exception.__class__.__name__
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

        for trait_name, trait in resource.traits().items():
            if getattr(resource, trait_name) is Absent:
                continue

            if isinstance(trait, OneOf):
                fragment = getattr(resource, trait_name)
                d[trait_name] = self.serialize_resource(fragment)
            else:
                d[trait_name] = getattr(resource, trait_name)

        return d
