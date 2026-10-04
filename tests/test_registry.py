from pydantic import BaseModel

from sigit.core.base import BaseService, Category
from sigit.core.registry import ServiceRegistry


def test_registry_discovery() -> None:
    services = ServiceRegistry.all()
    assert len(services) >= 14

    for name, svc_cls in services.items():
        assert issubclass(svc_cls, BaseService)
        assert svc_cls.name == name
        assert isinstance(svc_cls.description, str) and svc_cls.description
        assert isinstance(svc_cls.category, Category)
        assert issubclass(svc_cls.input_schema, BaseModel)


def test_service_category_filtering() -> None:
    network_services = ServiceRegistry.by_category(Category.NETWORK)
    assert len(network_services) >= 2
    for svc in network_services:
        assert svc.category == Category.NETWORK
