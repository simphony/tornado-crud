from collections import OrderedDict

from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.resource_handler import ResourceHandler


class WorkingResource(ResourceHandler):

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create(self, representation):
        id = type(self).id
        self.collection[str(id)] = representation
        type(self).id += 1
        return id

    @gen.coroutine
    def retrieve(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        return self.collection[identifier]

    @gen.coroutine
    def update(self, identifier, representation):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        self.collection[identifier] = representation

    @gen.coroutine
    def delete(self, identifier):
        if identifier not in self.collection:
            raise exceptions.NotFound()

        del self.collection[identifier]

    @gen.coroutine
    def items(self):
        return list(self.collection.keys())


class Student(WorkingResource):
    pass


class Teacher(ResourceHandler):
    @gen.coroutine
    def retrieve(self, identifier):
        return {}

    @gen.coroutine
    def items(self):
        return []


class UnsupportAll(ResourceHandler):
    pass


class Unprocessable(ResourceHandler):
    @gen.coroutine
    def create(self, representation):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def update(self, identifier, representation):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def retrieve(self, identifier):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def items(self):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")


class UnsupportsCollection(ResourceHandler):
    @gen.coroutine
    def items(self):
        raise NotImplementedError()


class Broken(ResourceHandler):
    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class ExceptionValidated(ResourceHandler):
    def validate_representation(self, representation):
        raise Exception("woo!")


class OurExceptionValidated(ResourceHandler):
    def validate_representation(self, representation):
        raise exceptions.BadRepresentation("woo!")


class NullReturningValidated(ResourceHandler):
    def validate_representation(self, representation):
        pass


class CorrectValidated(WorkingResource):
    def validate_representation(self, representation):
        representation["hello"] = 5
        return representation


class AlreadyPresent(ResourceHandler):
    @gen.coroutine
    def create(self, *args):
        raise exceptions.Exists()


class InvalidIdentifier(ResourceHandler):
    def validate_identifier(self, identifier):
        raise Exception("woo!")


class OurExceptionInvalidIdentifier(ResourceHandler):
    def validate_identifier(self, identifier):
        raise exceptions.BadRepresentation("woo!")


class Sheep(ResourceHandler):
    """Sheep plural is the same as singular."""
    __collection_name__ = "sheep"
    pass


class Octopus(ResourceHandler):
    """Octopus plural is a matter of debate."""
    __collection_name__ = "octopi"
    pass
