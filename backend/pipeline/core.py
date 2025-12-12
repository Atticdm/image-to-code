from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Generic, List, TypeVar

from fastapi import WebSocket

C = TypeVar("C")


class Middleware(ABC, Generic[C]):
    @abstractmethod
    async def process(
        self, context: C, next_func: Callable[[], Awaitable[None]]
    ) -> None:
        pass


class Pipeline(Generic[C]):
    def __init__(self, context_factory: Callable[[WebSocket], C]):
        self._context_factory = context_factory
        self.middlewares: List[Middleware[C]] = []

    def use(self, middleware: Middleware[C]) -> "Pipeline[C]":
        self.middlewares.append(middleware)
        return self

    async def execute(self, websocket: WebSocket) -> None:
        context = self._context_factory(websocket)

        async def start(_: C):
            return

        chain: Callable[[C], Awaitable[None]] = start
        for middleware in reversed(self.middlewares):
            chain = self._wrap_middleware(middleware, chain)

        await chain(context)

    def _wrap_middleware(
        self,
        middleware: Middleware[C],
        next_func: Callable[[C], Awaitable[None]],
    ) -> Callable[[C], Awaitable[None]]:
        async def wrapped(context: C) -> None:
            await middleware.process(context, lambda: next_func(context))

        return wrapped

