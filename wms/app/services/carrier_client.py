from dataclasses import dataclass
from typing import Protocol

from app.core.config import get_settings


@dataclass
class LabelResult:
    label_bytes: bytes
    tracking_number: str


class CarrierProvider(Protocol):
    def create_label(self, shipment) -> LabelResult:  # pragma: no cover - interface definition
        ...


_settings = get_settings()


def get_provider() -> CarrierProvider:
    provider_name = _settings.carrier_provider.lower()
    if provider_name == "aggregator":
        from app.services.carrier_providers.aggregator import AggregatorProvider

        return AggregatorProvider()
    if provider_name == "ups":
        from app.services.carrier_providers.ups import UPSProvider

        return UPSProvider()
    if provider_name == "usps":
        from app.services.carrier_providers.usps import USPSProvider

        return USPSProvider()
    if provider_name == "fedex":
        from app.services.carrier_providers.fedex import FedExProvider

        return FedExProvider()
    from app.services.carrier_providers.aggregator import AggregatorProvider

    return AggregatorProvider()
