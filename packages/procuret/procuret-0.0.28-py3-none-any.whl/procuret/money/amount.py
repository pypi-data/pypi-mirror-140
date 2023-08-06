"""
Procuret Python
Amount Module
author: hugh@blinkybeach.com
"""
from procuret.data.codable import Codable, CodingDefinition as CD
from procuret.money.currency import Currency
from decimal import Decimal
from typing import Type, TypeVar, List

T = TypeVar('T', bound='Amount')


class Amount(Codable):

    coding_map = {
        'magnitude': CD(Decimal),
        'denomination': CD(Currency)
    }

    def __init__(
        self,
        magnitude: Decimal,
        denomination: Currency
    ) -> None:

        self._magnitude = magnitude
        self._denomination = denomination

        return

    magnitude = property(lambda s: s._magnitude)
    denomination = property(lambda s: s._denomination)

    pretty_magnitude = property(
        lambda s: '{:,}'.format(s._magnitude)
    )

    @classmethod
    def denominations_are_homogenous(
        cls: Type[T],
        amounts: List[T]
    ) -> bool:
        unique = set(amounts)
        if len(unique) > 1:
            return False
        return True
