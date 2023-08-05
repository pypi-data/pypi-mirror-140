import pywaves as pw
from pydantic import BaseModel


class NewAccount(BaseModel):
    address: str
    private_key: str
    seed: str


def generate_new_account() -> NewAccount:
    random_valid_address = "3PJxgif9UrAgrp5XHJuMCHRvKGeHUR69DGq"  # noqa
    new_acc = pw.Address(address=random_valid_address)
    new_acc._generate()  # noqa
    return NewAccount(address=new_acc.address, private_key=new_acc.privateKey, seed=new_acc.seed)


def get_address_from_private_key(private_key: str) -> str:
    acc = pw.Address(privateKey=private_key)
    return acc.address


def check_private_key(address: str, private_key: str) -> bool:
    try:
        acc = pw.Address(privateKey=private_key)
        return acc.address == address
    except Exception:  # noqa
        return False


def is_valid_address(address: str) -> bool:
    return pw.validateAddress(address)
