from ..Classes.Auto import AutoCompareClass


class BaseTypes(AutoCompareClass):
    _compare_attrs = ('value',)

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)


class Null(BaseTypes):
    ...


class OneType(BaseTypes):
    def __init__(self, value):
        super().__init__(value=value)


class ArrayType(BaseTypes):
    def __init__(self, value=None):
        super().__init__(value=value if value is not None else [])

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def __str__(self):
        return str(self.value)


class MapType(BaseTypes):
    def __init__(self, value=None):
        super().__init__(value=value if value is not None else {})

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def __str__(self):
        return str(self.value)


class UserDefinedStructType(BaseTypes):
    def __init__(self, value=None):
        super().__init__(value=value)

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value})"

    def __str__(self):
        return str(self.value)


class String(OneType):
    def __init__(self, string):
        super().__init__(value=string)


class Int(OneType):
    def __init__(self, value: str | int | float):
        super().__init__(value)
        if isinstance(value, (int, float)):
            self.value = int(value)
        elif isinstance(value, str):
            try:
                self.value = int(value)
            except ValueError:
                raise ValueError("Invalid integer value")
        else:
            raise TypeError("Invalid type for integer value")


class Float(OneType):
    def __init__(self, value: str | int | float):
        super().__init__(value)
        if isinstance(value, (int, float)):
            self.value = float(value)
        elif isinstance(value, str):
            try:
                self.value = float(value)
            except ValueError:
                raise ValueError("Invalid float value")
        else:
            raise TypeError("Invalid type for float value")


class Bool(OneType):
    def __init__(self, value: str | bool):
        super().__init__(value)
        if isinstance(value, bool):
            self.value = value
        elif isinstance(value, str):
            value = value.strip().lower()
            if value == 'true':
                self.value = True
            elif value == 'false':
                self.value = False
            else:
                raise ValueError("Invalid boolean value")
        else:
            raise TypeError("Invalid type for boolean value")


class List(ArrayType):
    def __init__(self, value: list[BaseTypes | ArrayType] = None):
        super().__init__(value=value if value is not None else [])


class Tuple(ArrayType):
    def __init__(self, value: tuple[BaseTypes | ArrayType] = None):
        super().__init__(value=value if value is not None else tuple())


class Dict(MapType):
    def __init__(self, value: dict[BaseTypes | ArrayType, BaseTypes | ArrayType] = None):
        super().__init__(value=value if value is not None else {})
