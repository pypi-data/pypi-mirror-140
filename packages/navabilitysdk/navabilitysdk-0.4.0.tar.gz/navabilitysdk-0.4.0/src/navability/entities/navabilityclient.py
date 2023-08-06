from dataclasses import dataclass

from gql import Client as GQLCLient
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport


@dataclass(frozen=True)
class QueryOptions:
    query: str
    variables: any = None
    fetchPolicy: any = None


@dataclass(frozen=True)
class MutationOptions:
    mutation: str
    variables: any = None
    fetchPolicy: any = None


class NavAbilityClient:
    def query(self, options: QueryOptions):
        pass

    def mutate(self, options: MutationOptions):
        pass


class NavAbilityWebsocketClient(NavAbilityClient):
    def __init__(self, url: str = "wss://api.d1.navability.io/graphql") -> None:
        super().__init__()
        self.transport = WebsocketsTransport(url=url)

    async def query(self, options: QueryOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=False
        ) as client:
            result = await client.execute(options.query, options.variables)
            return result

    async def mutate(self, options: MutationOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=False
        ) as client:
            result = await client.execute(options.mutation, options.variables)
            return result


class NavAbilityHttpsClient(NavAbilityClient):
    def __init__(self, url: str = "https://api.d1.navability.io") -> None:
        super().__init__()
        self.transport = AIOHTTPTransport(url=url)

    async def query(self, options: QueryOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=True
        ) as client:
            result = await client.execute(options.query, options.variables)
            return result

    async def mutate(self, options: MutationOptions):
        async with GQLCLient(
            transport=self.transport, fetch_schema_from_transport=True
        ) as client:
            result = await client.execute(options.mutation, options.variables)
            return result
