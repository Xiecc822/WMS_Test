from app.services.carrier_client import LabelResult


class FedExProvider:
    def create_label(self, shipment) -> LabelResult:
        from app.services.carrier_providers.aggregator import AggregatorProvider

        return AggregatorProvider().create_label(shipment)
