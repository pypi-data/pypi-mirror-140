import sys
# pip install typing-extensions
from typing import _type_check

from typing_extensions import _TypedDictMeta


class _DefTypeDictMeta(_TypedDictMeta):
    def __new__(cls, name, bases, ns, total=True):
        """Create new typed dict class object.

        This method is called when TypedDict is subclassed,
        or when TypedDict is instantiated. This way
        TypedDict supports all three syntax forms described in its docstring.
        Subclasses and instances of TypedDict return actual dictionaries.
        """
        for base in bases:
            if type(base) is not _DefTypeDictMeta:
                raise TypeError('cannot inherit from both a DefTypeDict type '
                                'and a non-TypedDict base class')
        tp_dict = type.__new__(_DefTypeDictMeta, name, (dict,), ns)

        annotations = {}
        own_annotations = ns.get('__annotations__', {})
        own_annotation_keys = set(own_annotations.keys())
        msg = "DefTypeDict('Name', {f0: t0, f1: t1, ...}); each t must be a type"
        own_annotations = {
            n: _type_check(tp, msg, module=tp_dict.__module__)
            for n, tp in own_annotations.items()
        }
        required_keys = set()
        optional_keys = set()

        for base in bases:
            annotations.update(base.__dict__.get('__annotations__', {}))
            required_keys.update(base.__dict__.get('__required_keys__', ()))
            optional_keys.update(base.__dict__.get('__optional_keys__', ()))

        annotations.update(own_annotations)
        if total:
            required_keys.update(own_annotation_keys)
        else:
            optional_keys.update(own_annotation_keys)

        tp_dict.__annotations__ = annotations
        tp_dict.__required_keys__ = frozenset(required_keys)
        tp_dict.__optional_keys__ = frozenset(optional_keys)
        if not hasattr(tp_dict, '__total__'):
            tp_dict.__total__ = total
        return tp_dict

    def default_dit(self, **kwargs):
        return {_k: _v for _k, _v
                in self.__dict__.items() if
                not _k.startswith("__") and
                not _k.endswith("__") and
                _k not in kwargs} | kwargs

    __call__ = default_dit  # dict  # static method


def DefTypeDict(typename, fields=None, /, *, total=True, **kwargs):
    """
    Словарь поддерживающий значения по умолчанию

    >>> class Settings(DefTypeDict):
    >>>    port: int = 7070
    >>>    host: str = "0.0.0.0"
    >>> Settings(port=8080)
    {"port":8080, host="0.0.0.0"}

    @param typename:
    @param fields:
    @param total:
    @param kwargs:
    @return:
    """

    if fields is None:
        fields = kwargs
    elif kwargs:
        raise TypeError("DefTypeDict takes either a dict or keyword arguments,"
                        " but not both")

    ns = {'__annotations__': dict(fields)}
    try:
        # Setting correct module is necessary to make typed dict classes pickleable.
        ns['__module__'] = sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return _DefTypeDictMeta(typename, (), ns, total=total)


_DefTypeDict = type.__new__(_DefTypeDictMeta, 'DefTypeDict', (), {})
DefTypeDict.__mro_entries__ = lambda bases: (_DefTypeDict,)
