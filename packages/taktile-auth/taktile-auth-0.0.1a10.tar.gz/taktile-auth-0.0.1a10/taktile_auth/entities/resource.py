from __future__ import annotations

import re
import typing as t

import pydantic

from taktile_auth.enums import Wildcard

PARTIAL_RE = re.compile(r"(^[^\*]*$)|(^[^\*]*\*$)")


def is_full_wildcard(v):
    assert v == "*" or "*" not in v
    return v


def is_partial_wildcard(v):
    assert re.fullmatch(PARTIAL_RE, v)
    return v


def is_full_specified(v):
    assert "*" not in v
    return v


WILDCARD_CHECK = {
    Wildcard.allowed: is_full_wildcard,
    Wildcard.partial: is_partial_wildcard,
    Wildcard.not_allowed: is_full_specified,
}


class Resource(pydantic.BaseModel):
    def __contains__(self, o: Resource) -> bool:
        """Checks if the queried resource 'o' is either equal
        or contained inside of 'self'.
        For each arg of the resource, checks if it is either a
        match with query's corresponding arg (including wildcards).
        """
        for arg in self.dict().keys():
            allowed = getattr(self, arg)
            queried = getattr(o, arg)
            if not re.fullmatch(allowed.replace("*", ".*"), queried):
                return False
        return True

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class ResourceDefinition(pydantic.BaseModel):
    resource_name: str
    args: t.Dict[str, Wildcard]

    def get_resource(self) -> Resource:
        fields = {field_name: (str, ...) for field_name in self.args.keys()}
        validators = {
            f"{field_name}_validator": (
                pydantic.validator(field_name, allow_reuse=True)(
                    WILDCARD_CHECK[check]
                )
            )
            for field_name, check in self.args.items()
        }
        return pydantic.create_model(
            self.resource_name,
            **fields,
            __validators__=validators,
            __base__=Resource,
        )
