"""NanamiLang Python 3 Interop Classes"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang import shortcuts
from ._exports import export
from .base import Base
from .type import Type
from .nil import Nil
from .boolean import Boolean
from .string import String
from .floatnumber import FloatNumber
from .integernumber import IntegerNumber
from .keyword import Keyword
from .vector import Vector
from .symbol import Symbol


class Py3Inst(Base):
    """NanamiLang Python 3 object type"""

    name = 'Py3Inst'
    _expected_type = object
    _python_reference = object
    _object_name: str
    purpose = 'Encapsulate Python 3 object'

    def __init__(self, reference) -> None:
        """Initialize new NanamiLang Py3Inst instance"""

        self._object_name = reference.__class__.__name__

        super().__init__(reference)

    def _set_hash(self, reference) -> None:
        """NanamiLang Py3Inst, overrides self._set_hash"""

        hashed = getattr(reference, 'hashed', None)
        self._hashed = (
            hashed() if hashed else hash(reference.__class__))

        # NOTE: comparing two instances of the same class will
        #       always return true
        # NOTE: also, it's not reasonable to use the instances
        #       in Hash* structs as their hashes aren't unique
        # NOTE: so Py3Object can be equal to Py3Inst sometimes
        #       ,and you need to check (.instance) of instance

        # In order to be compatible with the other data types.

    def get(self,
            symbol: Keyword, default=None
            ) -> ('Py3Inst' or 'Py3Object' or Nil):
        """NanamiLang Py3Inst, returns Py3Inst or Py3Object"""

        if not default:
            default = Nil('nil')

        shortcuts.ASSERT_IS_CHILD_OF(
            symbol,
            Keyword,
            message='Py3Inst.get: symbol name is not a Keyword'
        )

        name = shortcuts.demangle(symbol.reference())

        attribute = getattr(self.reference(), name, None)

        # For now, we implicitly dispatch Py3Inst & Py3Object
        # depending on existence of the '__call__()' attribute

        return (Py3Object(attribute)
                if hasattr(attribute, '__call__')
                else Py3Inst(attribute)) if attribute else default

    def format(self, **_) -> str:
        """NanamiLang Py3Inst, 'format()' method implementation"""

        return f'<{self._object_name}>'

    @export()
    def instance(self) -> Type:
        """NanamiLang Py3Inst, 'instance()' method implementation"""

        return Type(Type.Py3Inst)

    @export()
    def cast(self, to: Keyword) -> Base:
        """NanamiLang Py3Inst, cast Py3Inst tp NanamiLang data type"""

        # As for now, we only support simple data types to cast into

        shortcuts.ASSERT_IS_CHILD_OF(
            to,
            Keyword,
            message='Py3Inst.cast: type name to cast to is not a Keyword'
        )

        conv = lambda: self.reference().decode('utf-8') \
            if isinstance(self.reference(), bytes) else str(self.reference())

        if to.reference() == 'to-auto':
            if isinstance(self.reference(), (str,
                                             bytes)):
                return String(conv())
            if isinstance(self.reference(), bool):
                return Boolean(self.reference())
            if isinstance(self.reference(), float):
                return FloatNumber(self.reference())
            if isinstance(self.reference(), int):
                return IntegerNumber(self.reference())
            return Nil('nil')  # return nil instead of AssertionError raising
        if to.reference() == 'to-string':
            return String(conv())
        if to.reference() == 'to-symbol':
            return Symbol(conv())
        if to.reference() == 'to-keyword':
            return Keyword(conv())
        if to.reference() == 'to-boolean':
            return Boolean(bool(self.reference()))
        if to.reference() == 'to-float-number':
            return FloatNumber(float(self.reference()))
        if to.reference() == 'to-integer-number':
            return IntegerNumber(int(self.reference()))
        # Should only be used when Py3Inst holds 'datatypes.*'
        # For instance, 'eval' function from standard library could use this.
        if (to.reference() == 'to-encapsulated' and
                issubclass(self.reference().__class__, (Base,))):
            return self.reference()  # thus, only return if a valid data type

        raise AssertionError('Py3Inst.cast: could not cast self.reference()')


class Py3Object(Base):
    """NanamiLang Python 3 object instance type"""

    name = 'Py3Object'
    _expected_type = object
    _python_reference = object
    _object_name: str
    purpose = 'Encapsulate Python 3 object instance'

    def __init__(self, reference) -> None:
        """Initialize new NanamiLang Py3Object instance"""

        self._object_name = reference.__name__

        super().__init__(reference)

    def _set_hash(self, reference) -> None:
        """NanamiLang Py3Object, overrides self._set_hash"""

        hashed = getattr(reference, 'hashed', None)
        self._hashed = hashed() if hashed else hash(reference)

        # In order to be compatible with the other data types.

    def get(self,
            symbol: Keyword, default=None
            ) -> ('Py3Inst' or 'Py3Object' or Nil):
        """NanamiLang Py3Object, returns Py3Inst or Py3Object"""

        if not default:
            default = Nil('nil')

        shortcuts.ASSERT_IS_CHILD_OF(
            symbol,
            Keyword,
            message='Py3Object.get: symbol name is not a Keyword'
        )

        name = shortcuts.demangle(symbol.reference())

        attribute = getattr(self.reference(), name, None)

        # For now, we implicitly dispatch Py3Inst & Py3Object
        # depending on existence of the '__call__()' attribute

        return (Py3Object(attribute)
                if hasattr(attribute, '__call__')
                else Py3Inst(attribute)) if attribute else default

    def format(self, **_) -> str:
        """NanamiLang Py3Object, 'format()' method implementation"""

        return f'<{self._object_name}>'

    @export()
    def instance(self) -> Type:
        """NanamiLang Py3Object, 'instance()' method implementation"""

        return Type(Type.Py3Object)

    @export()
    def instantiate(self, args: Vector) -> Py3Inst:
        """NanamiLang Py3Object, 'instantiate()' method implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            args,
            Vector,
            message='Py3Object.instantiate: instantiate args argument is not a Vector'
        )

        return Py3Inst(self.reference()(*[item.reference() for item in args.items()]))
