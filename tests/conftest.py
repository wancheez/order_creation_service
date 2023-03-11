import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers

from order_service.adapters.orm import mapper_registry, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:", echo=True)
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def engine(in_memory_db):
    start_mappers()
    yield in_memory_db
    clear_mappers()
