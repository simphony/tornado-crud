from collections import OrderedDict

from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.resource import Resource


class Student(Resource):

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


class Teacher(Resource):
    @gen.coroutine
    def retrieve(self, identifier):
        return {}

    @gen.coroutine
    def items(self):
        return []


class UnsupportAll(Resource):
    pass


class Unprocessable(Resource):
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


class UnsupportsCollection(Resource):
    @gen.coroutine
    def items(self):
        raise NotImplementedError()


class Broken(Resource):
    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class Validated(Resource):
    def validate(self, representation):
        raise Exception("woo!")


class AlreadyPresent(Resource):
    @gen.coroutine
    def create(self, *args):
        raise exceptions.Exists()


class Sheep(Resource):
    """Sheep plural is the same as singular."""
    __collection_name__ = "sheep"
    pass


class Octopus(Resource):
    """Octopus plural is a matter of debate."""
    __collection_name__ = "octopi"
    pass
