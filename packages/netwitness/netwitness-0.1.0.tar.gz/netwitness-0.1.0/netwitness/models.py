from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID
from ipaddress import IPv4Address


def _to_camel(string: str) -> str:
    exploded = string.split("_")
    return exploded[0] + "".join(word.capitalize() for word in exploded[1:])


class Host(BaseModel):
    id: UUID = Field(..., alias="_id")
    ipv4: IPv4Address
    ipv4_public: Optional[IPv4Address]
    third_party: bool
    display_name: Optional[str]
    installed_services: List[str]

    class Config:
        alias_generator = _to_camel

    @validator("ipv4_public", pre=True)
    def _allow_no_public(cls, v):
        if len(v) == 0:
            return None
        return v
