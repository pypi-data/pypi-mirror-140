import json

from tests.utils import fixtures_path
from hestia_earth.validation.validators.product import (
    validate_economicValueShare, validate_value, validate_excreta, validate_primary
)


def test_validate_economicValueShare_valid():
    # no products should be valid
    assert validate_economicValueShare([]) is True

    with open(f"{fixtures_path}/product/economicValueShare/valid.json") as f:
        data = json.load(f)
    assert validate_economicValueShare(data.get('nodes')) is True


def test_validate_economicValueShare_invalid():
    with open(f"{fixtures_path}/product/economicValueShare/invalid.json") as f:
        data = json.load(f)
    assert validate_economicValueShare(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.products',
        'message': 'economicValueShare should sum to 100 or less across all products',
        'params': {
            'sum': 110
        }
    }


def test_validate_value_valid():
    # no products should be valid
    assert validate_value([]) is True

    with open(f"{fixtures_path}/product/value/valid.json") as f:
        data = json.load(f)
    assert validate_value(data.get('nodes')) is True


def test_validate_value_warning():
    with open(f"{fixtures_path}/product/value/warning.json") as f:
        data = json.load(f)
    assert validate_value(data.get('nodes')) == {
        'level': 'warning',
        'dataPath': '.products[1]',
        'message': 'may not be 0'
    }


def test_validate_excreta_valid():
    # no products should be valid
    assert validate_excreta({}) is True

    with open(f"{fixtures_path}/product/excreta/valid.json") as f:
        data = json.load(f)
    assert validate_excreta(data) is True

    with open(f"{fixtures_path}/product/excreta/valid-no-excreta.json") as f:
        data = json.load(f)
    assert validate_excreta(data) is True


def test_validate_excreta_warning():
    with open(f"{fixtures_path}/product/excreta/warning.json") as f:
        data = json.load(f)
    assert validate_excreta(data) == {
        'level': 'warning',
        'dataPath': '.products[1].term.@id',
        'message': 'is too generic',
        'params': {
            'product': {
                '@type': 'Term',
                '@id': 'meatChickenLiveweight',
                'termType': 'animalProduct'
            },
            'term': {
                '@type': 'Term',
                '@id': 'excretaKgN',
                'termType': 'excreta'
            },
            'current': 'excretaKgN',
            'expected': 'excretaPoultryKgN'
        }
    }


def test_validate_primary_valid():
    # no products should be valid
    assert validate_primary([]) is True

    with open(f"{fixtures_path}/product/primary/valid.json") as f:
        data = json.load(f)
    assert validate_primary(data.get('nodes')) is True


def test_validate_primary_error():
    with open(f"{fixtures_path}/product/primary/invalid.json") as f:
        data = json.load(f)
    assert validate_primary(data.get('nodes')) == {
        'level': 'error',
        'dataPath': '.products',
        'message': 'only 1 primary product allowed'
    }
