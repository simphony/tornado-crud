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
    def create(self, instance):
        id = type(self).id
        self.collection[str(id)] = instance
        instance.identifier = str(id)
        type(self).id += 1
        return id

    @gen.coroutine
    def retrieve(self, instance):
        if instance.identifier not in self.collection:
            raise exceptions.NotFound()

        stored_item = self.collection[instance.identifier]
        for trait_name, trait_class in instance.traits().items():
            setattr(instance, trait_name, getattr(stored_item, trait_name))

    @gen.coroutine
    def update(self, instance):
        if instance.identifier not in self.collection:
            raise exceptions.NotFound()

        self.collection[instance.identifier] = instance

    @gen.coroutine
    def delete(self, instance):
        if instance.identifier not in self.collection:
            raise exceptions.NotFound()

        del self.collection[instance.identifier]

    @gen.coroutine
    def items(self, args):
        print(args)
        return list(self.collection.values())


class Student(Resource):
    name = Unicode()
    age = Int()


class StudentHandler(WorkingResourceHandler):
    resource_class = Student


class Teacher(Resource):
    name = Unicode()
    age = Int(optional=True)
    discipline = List()


class TeacherHandler(ResourceHandler):
    resource_class = Teacher


class UnsupportAll(Resource):
    pass


class UnsupportAllHandler(ResourceHandler):
    resource_class = UnsupportAll


class Unprocessable(Resource):
    pass


class UnprocessableHandler(ResourceHandler):
    resource_class = Unprocessable

    @gen.coroutine
    def create(self, instance):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def update(self, instance):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def retrieve(self, instance):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def items(self):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")


class UnsupportsCollection(Resource):
    pass


class UnsupportsCollectionHandler(ResourceHandler):
    resource_class = UnsupportsCollection

    @gen.coroutine
    def items(self):
        raise NotImplementedError()


class Broken(Resource):
    pass


class BrokenHandler(ResourceHandler):
    resource_class = Broken

    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class ExceptionValidated(Resource):
    pass


class ExceptionValidatedHandler(ResourceHandler):
    resource_class = ExceptionValidated

    def preprocess_representation(self, representation):
        raise Exception("woo!")


class OurExceptionValidated(Resource):
    pass


class OurExceptionValidatedHandler(ResourceHandler):
    resource_class = OurExceptionValidated

    def preprocess_representation(self, representation):
        raise exceptions.BadRepresentation("woo!")


class NullReturningValidated(Resource):
    pass


class NullReturningValidatedHandler(ResourceHandler):
    resource_class = NullReturningValidated

    def preprocess_representation(self, representation):
        pass


class CorrectValidated(Resource):
    pass


class CorrectValidatedHandler(WorkingResourceHandler):
    resource_class = CorrectValidated

    def preprocess_representation(self, representation):
        representation["hello"] = 5
        return representation


class AlreadyPresent(Resource):
    pass


class AlreadyPresentHandler(ResourceHandler):
    resource_class = AlreadyPresent

    @gen.coroutine
    def create(self, *args):
        raise exceptions.Exists()


class InvalidIdentifier(Resource):
    pass


class InvalidIdentifierHandler(ResourceHandler):
    resource_class = InvalidIdentifier

    def preprocess_identifier(self, identifier):
        raise Exception("woo!")


class OurExceptionInvalidIdentifier(Resource):
    pass


class OurExceptionInvalidIdentifierHandler(ResourceHandler):
    resource_class = OurExceptionInvalidIdentifier

    def preprocess_identifier(self, identifier):
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


class WrongClassHandler(ResourceHandler):
    resource_class = str


class ItemsReturnsString(Resource):
    pass


class ItemsReturnsStringHandler(ResourceHandler):
    resource_class = ItemsReturnsString

    @gen.coroutine
    def items(self):
        return "hello"


class ReturnsIncorrectType(Resource):
    pass


class ReturnsIncorrectTypeHandler(ResourceHandler):
    resource_class = ReturnsIncorrectType

    @gen.coroutine
    def items(self):
        return ["hello"]
