from dataclasses import dataclass


@dataclass
class Address:
    zipCode: str
    houseNumber: int
    houseNumberExtension: str | None
    city: str
    street: str


@dataclass
class Contract:
    id: int
    relationId: int
    propositionType: str
    contractStatus: str
    contractType: str
    supplyAddress: Address
