from tornadowebapi.base_schema import BaseSchema
from tornadowebapi.traitlets import Absent, OneOf

from marshmallow import class_registry
from marshmallow.base import SchemaABC
from marshmallow_jsonapi.fields import Relationship

from .exceptions import InvalidField, InvalidInclude


class Schema(BaseSchema):
    """A model representing a resource in our system.
    Must be reimplemented for the specific resource in our domain,
    as well as specifying its properties with traitlets.

    The following metadata in the specified traitlets are accepted:

    - optional
        bool, default False.
        If True, the information can be omitted from the representation
        when creating.
        If False, the information must be present, or an error
        BadRepresentation will be raised.
    - scope
        string
        Expresses the scope of the trait information. If specified, it accepts
        either of the two values:

            - "input": the trait is only relevant for the input representation
              and will be parsed, according to the other metadata, only during
              input operations. During output, the trait will not be present
              in the resulting representation, if specified.
            - "output": the trait is only relevant for the output
              representation. If specified during an input operation, it will
              be ignored.
            - If unspecified, the trait will be validated and accepted in both
              directions.

        Typical uses of scopes are:

            - you want to specify "readonly" information in your resource
              that you are not able to modify, but the server can return
              anyway. Example: the state of an operation. In that case, use
              "output"

            - you want to specify information that the client can specify,
              but the server does not want to (or cannot) return anymore.


    The resource is always identified via its collection name, and
    its identifier. Both will end up in the URL, like so

    /collection_name/identifier/

    """
    def __init__(self, identifier, *args, **kwargs):
        self.identifier = identifier

        super(Schema, self).__init__(*args, **kwargs)

    @classmethod
    def collection_name(cls):
        """Identifies the name of the collection. By REST convention, it is
        a plural form of the class name, so the default is the name of the
        class, lowercase, and with an "s" added at the end.

        Override this method to return a better pluralization.
        """
        return cls.__name__.lower() + "s"

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        if not (value is None or isinstance(value, str)):
            raise ValueError("Identifier must be a string. Got {}".format(
                type(value)
            ))

        self._identifier = value


# Not as members because we want to prevent collisions with actual
# resource subclass traits.
def mandatory_absents(resource, scope):
    """Returns a set of the trait names that are mandatory, but do not
    have a specified value (i.e. they are Absent).

    Parameters
    ----------
    resource: Schema or ResourceFragment
        The resource to check
    scope: str
        Valid values are "input" and "output". Perform the check as if the
        resource is primed for an input operation (e.g. coming in as a POST or
        PUT) or for an output one (e.g. a GET)
    """
    if scope not in ["input", "output"]:
        raise ValueError("Scope must be either input or output")

    if not isinstance(resource, (BaseSchema)):
        raise TypeError("Resource must be a BaseResource, "
                        "got {} {} instead".format(resource, type(resource)))

    res = set()
    for trait_name, trait in resource.traits().items():
        if trait.metadata.get("scope", scope) != scope:
            continue

        trait_optional = trait.metadata.get("optional", False)
        if getattr(resource, trait_name) == Absent:
            if not trait_optional:
                res.add(trait_name)
        elif isinstance(trait, OneOf):
            res.update([
                ".".join([trait_name, x]) for x in mandatory_absents(
                    getattr(resource, trait_name), scope)])

    return res


def is_valid(resource, scope):
    """
    Returns True if the resource is valid, False otherwise.
    Validity is defined as follows:
    - identifier is not None
    - mandatory_absents is empty
    """
    return (resource.identifier is not None and
            len(mandatory_absents(resource, scope)) == 0)


def compute_schema(schema_cls, default_kwargs, qs, include):
    """Compute a schema around compound documents and sparse fieldsets

    Parameters
    ----------
    schema_cls: Schema
        the schema class
    default_kwargs: dict
        the schema default kwargs
    qs: QueryStringManager
        the querystring
    include: list
        the relation field to include data from

    Returns
    -------
    schema: the schema computed
    """
    # manage include_data parameter of the schema
    schema_kwargs = default_kwargs
    schema_kwargs['include_data'] = tuple()

    if include:
        for include_path in include:
            field = include_path.split('.')[0]
            if field not in schema_cls._declared_fields:
                raise InvalidInclude("{} has no attribute {}".format(
                    schema_cls.__name__, field))
            elif not isinstance(schema_cls._declared_fields[field],
                                Relationship):
                raise InvalidInclude(
                    "{} is not a relationship attribute of {}".format(
                        field, schema_cls.__name__))
            schema_kwargs['include_data'] += (field, )

    # make sure id field is in only parameter unless marshamllow will raise
    # an Exception
    if schema_kwargs.get('only') is not None and 'id' not in \
            schema_kwargs['only']:
        schema_kwargs['only'] += ('id',)

    # create base schema instance
    schema = schema_cls(**schema_kwargs)

    # manage sparse fieldsets
    if schema.opts.type_ in qs.fields:
        # check that sparse fieldsets exists in the schema
        for field in qs.fields[schema.opts.type_]:
            if field not in schema.declared_fields:
                raise InvalidField("{} has no attribute {}".format(
                    schema.__class__.__name__, field))

        tmp_only = set(schema.declared_fields.keys()) & set(
            qs.fields[schema.opts.type_])
        if schema.only:
            tmp_only &= set(schema.only)
        schema.only = tuple(tmp_only)

        # make sure again that id field is in only parameter unless
        # marshamllow will raise an Exception
        if schema.only is not None and 'id' not in schema.only:
            schema.only += ('id',)

    # manage compound documents
    if include:
        for include_path in include:
            field = include_path.split('.')[0]
            relation_field = schema.declared_fields[field]
            related_schema_cls = schema.declared_fields[field].__dict__[
                '_Relationship__schema']
            related_schema_kwargs = {}
            if isinstance(related_schema_cls, SchemaABC):
                related_schema_kwargs['many'] = related_schema_cls.many
                related_schema_cls = related_schema_cls.__class__
            if isinstance(related_schema_cls, str):
                related_schema_cls = class_registry.get_class(
                    related_schema_cls)
            if '.' in include_path:
                related_include = ['.'.join(include_path.split('.')[1:])]
            else:
                related_include = None
            related_schema = compute_schema(related_schema_cls,
                                            related_schema_kwargs,
                                            qs,
                                            related_include)
            relation_field.__dict__['_Relationship__schema'] = related_schema

    return schema


def get_model_field(schema, field):
    """Get the model field of a schema field

    :param Schema schema: a marshmallow schema
    :param str field: the name of the schema field
    :return str: the name of the field in the model
    """
    if schema._declared_fields[field].attribute is not None:
        return schema._declared_fields[field].attribute
    return field


def get_relationships(schema):
    """Return relationship mapping from schema to model

    :param Schema schema: a marshmallow schema
    :param list: list of dict with schema field and model field
    """
    return {get_model_field(schema, key): key for (key, value) in
            schema._declared_fields.items()
            if isinstance(value, Relationship)}
