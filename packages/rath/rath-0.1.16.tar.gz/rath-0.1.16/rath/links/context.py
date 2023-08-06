import asyncio
from concurrent.futures import ThreadPoolExecutor
from koil.koil import Koil
from koil.loop import koil_gen
from rath.links.base import ContinuationLink
from rath.operation import GraphQLResult, Operation
from koil import unkoil


class SwitchAsyncLink(ContinuationLink):
    def __init__(self, **koilparams):
        super().__init__()
        self.__koil = Koil(**koilparams)

    async def aquery(self, operation: Operation) -> GraphQLResult:
        return await self.next.aquery(operation)

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        async for result in self.next.asubscribe(operation):
            yield result

    def query(self, operation: Operation) -> GraphQLResult:
        return unkoil(self.next.aquery, operation)

    def subscribe(self, operation: Operation) -> GraphQLResult:
        for result in koil_gen(self.next.asubscribe, operation):
            yield result

    def connect(self) -> None:
        self.__koil.__enter__()
        unkoil(self.next.aconnect, ensure_koiled=True)

    def disconnect(self) -> None:
        unkoil(self.next.adisconnect, ensure_koiled=True)
        self.__koil.__exit__(None, None, None)


class SwitchSyncLink(ContinuationLink):
    def __init__(self, excecutor=None) -> None:
        self.excecutor = excecutor or ThreadPoolExecutor()
        self._lock = asyncio.Lock()
        self.connected = False
        super().__init__()

    async def aconnect(self) -> None:
        self.e = self.excecutor.__enter__()
        self.connected = True

    async def aquery(self, operation: Operation) -> GraphQLResult:
        async with self._lock:
            if not self.connected:
                await self.aconnect()

        return await asyncio.wrap_future(self.e.submit(self.next.query, operation))

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError(
            "We need to fiqure this out yet. Normally a __next__ call here would be enough"
        )

    def query(self, operation: Operation) -> GraphQLResult:
        return self.next.query(operation)

    def subscribe(self, operation: Operation) -> GraphQLResult:
        for result in self.next.subscribe(operation):
            yield result

    async def aconnect(self) -> None:
        self.e = self.excecutor.__exit__()
        self.connected = False
