from collections import OrderedDict

from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.resource import Resource
from tornadowebapi.traitlets import Unicode, Int, List


class WorkingResourceHandler(ResourceHandler):
    """Base class for tests. Still missing the resource_class
    that must be set in the derived class."""

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


class Student(Resource):
    name = Unicode()
    age = Int()


class Teacher(Resource):
    name = Unicode()
    age = Int(optional=True)
    discipline = List()


class GenericResource(Resource):
    pass


class StudentHandler(WorkingResourceHandler):
    resource_class = Student


class TeacherHandler(ResourceHandler):
    resource_class = Teacher

    @gen.coroutine
    def retrieve(self, identifier):
        return {}

    @gen.coroutine
    def items(self):
        return []


class UnsupportAllHandler(ResourceHandler):
    resource_class = GenericResource


class UnprocessableHandler(ResourceHandler):
    resource_class = GenericResource

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


class UnsupportsCollectionHandler(ResourceHandler):
    resource_class = GenericResource

    @gen.coroutine
    def items(self):
        raise NotImplementedError()


class BrokenHandler(ResourceHandler):
    resource_class = GenericResource

    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class ExceptionValidatedHandler(ResourceHandler):
    resource_class = GenericResource

    def validate_representation(self, representation):
        raise Exception("woo!")


class OurExceptionValidatedHandler(ResourceHandler):
    resource_class = GenericResource

    def validate_representation(self, representation):
        raise exceptions.BadRepresentation("woo!")


class NullReturningValidatedHandler(ResourceHandler):
    resource_class = GenericResource

    def validate_representation(self, representation):
        pass


class CorrectValidatedHandler(WorkingResourceHandler):
    resource_class = GenericResource

    def validate_representation(self, representation):
        representation["hello"] = 5
        return representation


class AlreadyPresentHandler(ResourceHandler):
    resource_class = GenericResource

    @gen.coroutine
    def create(self, *args):
        raise exceptions.Exists()


class InvalidIdentifierHandler(ResourceHandler):
    resource_class = GenericResource

    def validate_identifier(self, identifier):
        raise Exception("woo!")


class OurExceptionInvalidIdentifierHandler(ResourceHandler):
    resource_class = GenericResource

    def validate_identifier(self, identifier):
        raise exceptions.BadRepresentation("woo!")


class Sheep(Resource):
    @classmethod
    def collection_name(cls):
        return "sheep"


class SheepHandler(ResourceHandler):
    """Sheep plural is the same as singular."""
    resource_class = Sheep


class Octopus(Resource):
    @classmethod
    def collection_name(cls):
        return "octopi"


class OctopusHandler(ResourceHandler):
    """Octopus plural is a matter of debate."""
    resource_class = Octopus


class Frobnicator(Resource):
    pass


class FrobnicatorHandler(ResourceHandler):
    """A weird name to test if it's kept"""
    resource_class = Frobnicator
