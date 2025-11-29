import os
from dataclasses import asdict, dataclass

from utils import JSONFile


@dataclass
class AbstractTable:
    name: str

    @classmethod
    def get_file_prefix(cls):
        return "".join(
            [
                c.lower() if c.islower() else "_" + c.lower()
                for c in cls.__name__
            ]
        )[1:]

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    @classmethod
    def get_json_path(cls):
        return os.path.join(
            "data", "static", f"{cls.get_file_prefix()}s.json"
        )

    @classmethod
    def get_json_file(cls):
        return JSONFile(cls.get_json_path())

    @classmethod
    def __get_d_list__(cls):
        return cls.get_json_file().read()

    @classmethod
    def list_all(cls):
        cls.prettify()
        d_list = cls.__get_d_list__()
        return [cls.from_dict(d) for d in d_list]

    @classmethod
    def from_name_safe(cls, name):
        o_list = cls.list_all()
        for o in o_list:
            if o.name == name:
                return o
        return None

    @classmethod
    def from_name(cls, name):
        o = cls.from_name_safe(name)
        if not o:
            raise ValueError(f"{cls.__name__} with name '{name}' not found")
        return o

    def __eq__(self, other):
        if not isinstance(other, AbstractTable):
            return False
        return asdict(self) == asdict(other)

    @classmethod
    def prettify(cls):
        json_file = cls.get_json_file()
        d_list = json_file.read()
        d_list.sort(key=lambda d: d["name"])
        json_file.write(d_list)
