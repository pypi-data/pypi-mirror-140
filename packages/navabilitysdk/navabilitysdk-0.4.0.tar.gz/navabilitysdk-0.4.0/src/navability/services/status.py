from gql import gql

from navability.common.queries import GQL_GETSTATUSLATEST, GQL_GETSTATUSMESSAGES
from navability.entities.navabilityclient import NavAbilityClient, QueryOptions
from navability.entities.statusmessage import StatusMessageSchema


async def getStatusMessages(navAbilityClient: NavAbilityClient, id: str):
    statusMessages = await navAbilityClient.query(
        QueryOptions(gql(GQL_GETSTATUSMESSAGES), {"id": id})
    )
    schema = StatusMessageSchema(many=True)
    return schema.load(statusMessages["statusMessages"])


async def getStatusLatest(navAbilityClient: NavAbilityClient, id: str):
    statusMessages = await navAbilityClient.query(
        QueryOptions(gql(GQL_GETSTATUSLATEST), {"id": id})
    )
    schema = StatusMessageSchema()
    return schema.load(statusMessages["statusLatest"])
