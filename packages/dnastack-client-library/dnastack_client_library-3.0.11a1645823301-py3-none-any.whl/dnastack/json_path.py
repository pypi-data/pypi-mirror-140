from typing import Any


class BrokenPropertyPathError(AttributeError):
    """ Raised when JsonPath can't retrieve the value at the given property path """
    def __init__(self, obj, path: str, visited_path: str, reason: str, parent = None):
        self.__obj = obj
        self.__path = path
        self.__visited_path = visited_path
        self.__reason = reason
        self.__parent = parent

        super().__init__()

    @property
    def obj(self):
        return self.__obj

    @property
    def visited_path(self):
        return self.__visited_path

    @property
    def reason(self):
        return self.__reason

    @property
    def parent(self):
        return self.__parent

    def __str__(self):
        return f'{type(self.__obj).__name__}: {self.__visited_path}: {self.__reason}'

    def __repr__(self):
        return self.__str__()



class JsonPath:
    @staticmethod
    def set(obj, path: str, value: Any):
        target_property_names = path.split(r'.')

        pointer = JsonPath.get(obj, '.'.join(target_property_names[:-1]), raise_error_on_null=True)

        visited_property_name = target_property_names[-1]
        setattr(pointer, visited_property_name, value)

    @staticmethod
    def get(obj, path: str, raise_error_on_null=False) -> Any:
        if not path:
            return obj

        visited_property_names = []
        target_property_names = path.split(r'.')

        parent = None
        pointer = obj

        while len(target_property_names) > 0:
            visited_property_name = target_property_names.pop(0)
            visited_property_names.append(visited_property_name)

            if not hasattr(pointer, visited_property_name):
                raise BrokenPropertyPathError(
                    obj,
                    path,
                    '.'.join(visited_property_names),
                    'The configuration does not have the specific property.',
                    parent
                )

            parent = pointer
            pointer = getattr(pointer, visited_property_name)

        if pointer is None and raise_error_on_null:
            raise BrokenPropertyPathError(
                obj,
                path,
                '.'.join(visited_property_names),
                'Null value',
                parent
            )

        return pointer
