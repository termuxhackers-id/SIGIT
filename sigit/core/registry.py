import importlib
import pkgutil

from sigit.core.base import BaseService, Category


class ServiceRegistry:
    _services: dict[str, type[BaseService]] = {}
    _ordered: list[type[BaseService]] = []
    _discovered: bool = False

    @classmethod
    def discover(cls) -> None:
        if cls._discovered:
            return

        import sigit.services as pkg

        for _, module_name, _ in pkgutil.walk_packages(pkg.__path__, prefix=f"{pkg.__name__}."):
            if "._" in module_name:
                continue

            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseService)
                    and attr is not BaseService
                    and hasattr(attr, "name")
                ):
                    cls._services[attr.name] = attr

        cls._ordered = sorted(cls._services.values(), key=lambda svc: svc.name)
        cls._discovered = True

    @classmethod
    def all(cls) -> dict[str, type[BaseService]]:
        cls.discover()
        return dict(cls._services)

    @classmethod
    def ordered(cls) -> list[type[BaseService]]:
        cls.discover()
        return list(cls._ordered)

    @classmethod
    def get(cls, name: str) -> type[BaseService] | None:
        cls.discover()
        return cls._services.get(name)

    @classmethod
    def by_category(cls, category: Category) -> list[type[BaseService]]:
        cls.discover()
        return [svc for svc in cls._ordered if svc.category == category]

    @classmethod
    def count(cls) -> int:
        cls.discover()
        return len(cls._services)
