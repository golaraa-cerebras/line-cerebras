from pydantic import BaseModel


class DummyEvent(BaseModel):
    pass


class SubDummyEvent(DummyEvent):
    """A subclass for testing matching events based on inheritance."""

    pass


class AnotherEvent(BaseModel):
    """An unrelated event class for testing event routing."""

    pass


class NumberEvent(BaseModel):
    """An event class with some data to operate or filter on."""

    value: int
