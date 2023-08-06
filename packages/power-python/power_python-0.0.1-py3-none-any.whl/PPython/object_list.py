from dataclasses import dataclass
from typing import List, Any, Union, NoReturn


class ObjectList:
    def __init__(self, value: List[object]):
        self.value: List[object] = value

    def get_object_by_spec(self, name: str, value: Any) -> Union[object, None]:
        for i in self.value:
            if getattr(i, name) == value:
                return i
        return None

    def get_all_objects_by_spec(self, name: str, value: Any) -> Union[List[object], List]:
        objects: List[object] = []
        for i in self.value:
            if getattr(i, name) == value:
                objects.append(i)
        return objects

    def add_object(self, object_to_add: object) -> NoReturn:
        self.value.append(object_to_add)

    def add_object_by_index(self, index: int, value: object) -> NoReturn:
        self.value.insert(index, value)

    def delete_object_by_index(self, index: int) -> NoReturn:
        del self.value[index]

    def delete_object(self, object_: object) -> NoReturn:
        self.value.remove(object_)

    def delete_by_object_name(self, name: str) -> NoReturn:
        for i in self.value:
            if i.__class__.__name__ == name:
                del self.value[self.value.index(i)]
                break

    def delete_all_by_object_name(self, name: str) -> NoReturn:
        for i in self.value:
            if i.__class__.__name__ == name:
                del self.value[self.value.index(i)]

    def get_by_object_name(self, name: str) -> object:
        for i in self.value:
            if i.__class__.__name__ == name:
                return i

    def get_all_by_object_name(self, name: str) -> List[object]:
        object_list: List[object] = []

        for i in self.value:
            if i.__class__.__name__ == name:
                object_list.append(i)

        return object_list

    def add_new_attr_by_index(self, index: int, name: str, value: Any) -> NoReturn:
        setattr(self.value[index].__class__, name, value)

    def __iter__(self):
        return self.value



@dataclass
class User:
    name: str
    password: str


test = ObjectList([User('Mark', '233'), User('Mak', '23ewdf3')])

print(test.get_object_by_spec('name', 'Mak'))
