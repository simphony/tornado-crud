from collections import OrderedDict

from tornado import gen
from tornadowebapi import exceptions
from tornadowebapi.schema_fragment import SchemaFragment
from tornadowebapi.model_connector import ModelConnector
from tornadowebapi.schema import Schema
from tornadowebapi.singleton_schema import SingletonSchema
from tornadowebapi.traitlets import Unicode, Int, List, OneOf
from tornadowebapi.web_handlers import ResourceDetails, ResourceList


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
    pass


class StudentDetails(ResourceDetails):
    schema = Student
    model_connector = StudentModelConn


class StudentList(ResourceList):
    schema = Student
    model_connector = StudentModelConn


class Teacher(Schema):
    name = Unicode()
    age = Int(optional=True)
    discipline = List()


class TeacherModelConn(ModelConnector):
    pass


class TeacherDetails(ResourceDetails):
    schema = Teacher
    model_connector = TeacherModelConn


class TeacherList(ResourceDetails):
    schema = Teacher
    model_connector = TeacherModelConn


class Person(SchemaFragment):
    name = Unicode()
    age = Int()


class City(Schema):
    name = Unicode()
    mayor = OneOf(Person)


class CityModelConn(WorkingModelConn):
    pass


class CityDetails(ResourceDetails):
    schema = City
    model_connector = CityModelConn


class ServerInfo(SingletonSchema):
    uptime = Int()
    status = Unicode()


class ServerInfoModelConn(SingletonModelConn):
    resource_class = ServerInfo


class ServerInfoDetails(ResourceDetails):
    schema = ServerInfo
    model_connector = ServerInfoModelConn


class UnsupportAll(Schema):
    pass


class UnsupportAllModelConn(ModelConnector):
    pass


class UnsupportAllDetails(ResourceDetails):
    schema = UnsupportAll
    model_connector = UnsupportAllModelConn


class Unprocessable(Schema):
    pass


class UnprocessableModelConn(ModelConnector):
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


class UnprocessableDetails(ResourceDetails):
    schema = Unprocessable
    model_connector = UnprocessableModelConn


class UnsupportsCollection(Schema):
    pass


class UnsupportsCollectionModelConn(ModelConnector):

    @gen.coroutine
    def items(self, items_response, offset=None, limit=None, **kwargs):
        raise NotImplementedError()


class UnsupportsCollectionList(ResourceList):
    schema = UnsupportsCollection
    model_connector = UnsupportsCollectionModelConn


class Broken(Schema):
    pass


class BrokenModelConn(ModelConnector):
    @gen.coroutine
    def boom(self, *args):
        raise Exception("Boom!")

    create = boom
    retrieve = boom
    update = boom
    delete = boom
    items = boom


class BrokenDetails(ResourceDetails):
    schema = Broken
    model_connector = BrokenModelConn


class ExceptionValidated(Schema):
    pass


class ExceptionValidatedModelConn(ModelConnector):
    def preprocess_representation(self, representation):
        raise Exception("woo!")


class ExceptionValidatedDetails(ResourceDetails):
    schema = ExceptionValidated
    model_connector = ExceptionValidatedModelConn


class OurExceptionValidated(Schema):
    pass


class OurExceptionValidatedModelConn(ModelConnector):
    def preprocess_representation(self, representation):
        raise exceptions.BadRepresentation("woo!")


class OurExceptionValidatedDetails(ResourceDetails):
    schema = OurExceptionValidated
    model_connector = OurExceptionValidatedModelConn


class NullReturningValidated(Schema):
    pass


class NullReturningValidatedModelConn(ModelConnector):
    def preprocess_representation(self, representation):
        pass


class NullReturningValidatedDetails(ResourceDetails):
    schema = NullReturningValidated
    model_connector = NullReturningValidatedModelConn


class CorrectValidated(Schema):
    pass


class CorrectValidatedModelConn(WorkingModelConn):

    def preprocess_representation(self, representation):
        representation["hello"] = 5
        return representation


class CorrectValidatedDetails(ResourceDetails):
    schema = CorrectValidated
    model_connector = CorrectValidatedModelConn


class AlreadyPresent(Schema):
    pass


class AlreadyPresentModelConn(ModelConnector):

    @gen.coroutine
    def create(self, *args, **kwargs):
        raise exceptions.Exists()


class AlreadyPresentDetails(ResourceDetails):
    schema = AlreadyPresent
    model_connector = AlreadyPresentModelConn


class InvalidIdentifier(Schema):
    pass


class InvalidIdentifierModelConn(ModelConnector):
    def preprocess_identifier(self, identifier):
        raise Exception("woo!")


class InvalidIdentifierDetails(ResourceDetails):
    schema = InvalidIdentifier
    model_connector = InvalidIdentifierModelConn


class OurExceptionInvalidIdentifier(Schema):
    pass


class OurExceptionInvalidIdentifierModelConn(ModelConnector):
    def preprocess_identifier(self, identifier):
        raise exceptions.BadRepresentation("woo!")


class OurExceptionInvalidIdentifierDetails(ResourceDetails):
    schema = OurExceptionInvalidIdentifier
    model_connector = OurExceptionInvalidIdentifierModelConn


class Sheep(Schema):
    @classmethod
    def collection_name(cls):
        return "sheep"


class SheepModelConn(ModelConnector):
    """Sheep plural is the same as singular."""


class SheepDetails(ResourceDetails):
    schema = Sheep
    model_connector = SheepModelConn


class Octopus(Schema):
    @classmethod
    def collection_name(cls):
        return "octopi"


class OctopusModelConn(ModelConnector):
    """Octopus plural is a matter of debate."""
    resource_class = Octopus


class OctopusDetails(ResourceDetails):
    schema = Octopus
    model_connector = OctopusModelConn


class Frobnicator(Schema):
    pass


class FrobnicatorModelConn(ModelConnector):
    """A weird name to test if it's kept"""


class FrobnicatorDetails(ResourceDetails):
    schema = Frobnicator
    model_connector = FrobnicatorModelConn


class WrongClassModelConn(ModelConnector):
    resource_class = str
