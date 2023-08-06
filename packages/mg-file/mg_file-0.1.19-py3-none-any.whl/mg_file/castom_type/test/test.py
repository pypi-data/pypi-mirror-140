from typing import TypedDict

from pydantic import BaseModel

from castom_type.base import DefTypeDict


class SS(BaseModel):
    port: int
    host: str


class Sett(TypedDict):
    port: int
    host: str


class Sett2(DefTypeDict):
    port: int = 7070
    host: str = "555"


if __name__ == '__main__':
    s = Sett(port=23, host=123)
    sw = Sett2(port=23, host=33333)
    sw2 = Sett2(port=23, host=33333)
    sw3 = Sett2(port=23, host=33333)
    print(sw)
    print(sw2)
    print(sw3)
