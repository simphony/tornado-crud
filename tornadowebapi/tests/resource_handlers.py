from collections import OrderedDict

from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.schema_fragment import SchemaFragment
from tornadowebapi.model_connector import ModelConnector
from tornadowebapi.schema import Schema
from tornadowebapi.singleton_schema import SingletonSchema
from tornadowebapi.traitlets import Unicode, Int, List, OneOf


class WorkingModelConn(ModelConnector):
    """Base class for tests. Still missing the resource_class
    that must be set in the derived class."""

    collection = OrderedDict()
    id = 0

    @gen.coroutine
    def create(self, instance, **kwargs):
        id = type(self).id
        self.collection[str(id)] = instance
        instance.identifier = str(id)
        type(self).id += 1

    @gen.coroutine
    def retrieve(self, instance, **kwargs):
        if instance.identifier not in self.collection:
            raise exceptions.NotFound()

        stored_item = self.collection[instance.identifier]
        for trait_name, trait_class in instance.traits().items():
            setattr(instance, trait_name, getattr(stored_item, trait_name))

    @gen.coroutine
    def update(self, instance, **kwargs):
        if instance.identifier not in self.collection:
            raise exceptions.NotFound()

        self.collection[instance.identifier] = instance

    @gen.coroutine
    def delete(self, instance, **kwargs):
        if instance.identifier not in self.collection:
            raise exceptions.NotFound()

        del self.collection[instance.identifier]

    @gen.coroutine
    def items(self, items_response,
              offset=None, limit=None, filter_=None, **kwargs):
        if offset is None:
            offset = 0

        start = offset

        if limit is None:
            end = None
        else:
            end = start + limit

        interval = slice(start, end)

        if filter_ is not None:
            values = [x for x in self.collection.values() if filter_(x)]
        else:
            values = [x for x in self.collection.values()]

        items_response.set(values[interval],
                           offset=start,
                           total=len(self.collection.values()))


class SingletonModelConn(ModelConnector):
    instance = {}

    @gen.coroutine
    def create(self, instance, **kwargs):
        self.instance['instance'] = instance

    @gen.coroutine
    def retrieve(self, instance, **kwargs):
        if "instance" not in self.instance:
            raise exceptions.NotFound()

        for trait_name, trait_class in instance.traits().items():
            setattr(instance, trait_name,
                    getattr(self.instance["instance"],
                            trait_name))

    @gen.coroutine
    def update(self, instance, **kwargs):
        if "instance" not in self.instance:
            raise exceptions.NotFound()

        self.instance["instance"] = instance

    @gen.coroutine
    def delete(self, instance, **kwargs):
        if "instance" not in self.instance:
            raise exceptions.NotFound()

        del self.instance["instance"]


class Student(Schema):
    name = Unicode()
    age = Int()


class StudentModelConn(WorkingModelConn):
    resource_class = Student


class Teacher(Schema):
    name = Unicode()
    age = Int(optional=True)
    discipline = List()


class TeacherModelConn(ModelConnector):
    resource_class = Teacher


class Person(SchemaFragment):
    name = Unicode()
    age = Int()


class City(Schema):
    name = Unicode()
    mayor = OneOf(Person)


class CityModelConn(WorkingModelConn):
    resource_class = City


class ServerInfo(SingletonSchema):
    uptime = Int()
    status = Unicode()


class ServerInfoModelConn(SingletonModelConn):
    resource_class = ServerInfo


class UnsupportAll(Schema):
    pass


class UnsupportAllModelConn(ModelConnector):
    resource_class = UnsupportAll


class Unprocessable(Schema):
    pass


class UnprocessableModelConn(ModelConnector):
    resource_class = Unprocessable

    @gen.coroutine
    def create(self, instance, **kwargs):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def update(self, instance, **kwargs):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def retrieve(self, instance, **kwargs):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")

    @gen.coroutine
    def items(self, items_response, offset=None, limit=None, **kwargs):
        raise exceptions.BadRepresentation("unprocessable", foo="bar")


class UnsupportsCollection(Schema):
    pass


class UnsupportsCollectionModelConn(ModelConnector):
    resource_class = UnsupportsCollection

    @gen.coroutine
    def items(self, items_response, offset=None, limit=None, **kwargs):
        raise NotImplementedError()


class Broken(Schema):
    pass


class BrokenModelConn(ModelConnector):
    resource_class = Broken

    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class ExceptionValidated(Schema):
    pass


class ExceptionValidatedModelConn(ModelConnector):
    resource_class = ExceptionValidated

    def preprocess_representation(self, representation):
        raise Exception("woo!")


class OurExceptionValidated(Schema):
    pass


class OurExceptionValidatedModelConn(ModelConnector):
    resource_class = OurExceptionValidated

    def preprocess_representation(self, representation):
        raise exceptions.BadRepresentation("woo!")


class NullReturningValidated(Schema):
    pass


class NullReturningValidatedModelConn(ModelConnector):
    resource_class = NullReturningValidated

    def preprocess_representation(self, representation):
        pass


class CorrectValidated(Schema):
    pass


class CorrectValidatedModelConn(WorkingModelConn):
    resource_class = CorrectValidated

    def preprocess_representation(self, representation):
        representation["hello"] = 5
        return representation


class AlreadyPresent(Schema):
    pass


class AlreadyPresentModelConn(ModelConnector):
    resource_class = AlreadyPresent

    @gen.coroutine
    def create(self, *args, **kwargs):
        raise exceptions.Exists()


class InvalidIdentifier(Schema):
    pass


class InvalidIdentifierModelConn(ModelConnector):
    resource_class = InvalidIdentifier

    def preprocess_identifier(self, identifier):
        raise Exception("woo!")


class OurExceptionInvalidIdentifier(Schema):
    pass


class OurExceptionInvalidIdentifierModelConn(ModelConnector):
    resource_class = OurExceptionInvalidIdentifier

    def preprocess_identifier(self, identifier):
        raise exceptions.BadRepresentation("woo!")


class Sheep(Schema):
    @classmethod
    def collection_name(cls):
        return "sheep"


class SheepModelConn(ModelConnector):
    """Sheep plural is the same as singular."""
    resource_class = Sheep


class Octopus(Schema):
    @classmethod
    def collection_name(cls):
        return "octopi"


class OctopusModelConn(ModelConnector):
    """Octopus plural is a matter of debate."""
    resource_class = Octopus


class Frobnicator(Schema):
    pass


class FrobnicatorModelConn(ModelConnector):
    """A weird name to test if it's kept"""
    resource_class = Frobnicator


class WrongClassModelConn(ModelConnector):
    resource_class = str
