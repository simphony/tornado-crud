from tornadowebapi.traitlets import OneOf
from traitlets import HasTraits


class BaseSchema(HasTraits):
    def fill(self, entity):
        """Fills the traits with data taken from the given
        entity.

        Parameters
        ----------

        entity: dict or object
            The entity to retrieve information from. If a dict, this method
            will search for keys equal to the trait names. Otherwise, it will
            use getattr.
        """
        # Prevent cyclic import
        from tornadowebapi.schema_fragment import SchemaFragment

        if isinstance(entity, dict):
            def getter(x, y):
                return x[y]
        else:
            getter = getattr

        for trait_name, trait in self.traits().items():
            try:
                value = getter(entity, trait_name)
            except (AttributeError, KeyError):
                continue

            if (isinstance(trait, OneOf) and
                    issubclass(trait.klass, SchemaFragment)):

                value = trait.klass()
                value.fill(getter(entity, trait_name))

            setattr(self, trait_name, value)
