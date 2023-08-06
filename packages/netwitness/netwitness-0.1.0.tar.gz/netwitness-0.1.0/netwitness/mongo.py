from motor.motor_asyncio import AsyncIOMotorClient
from . import ports


class TrustedMongoClient(AsyncIOMotorClient):
    def __init__(self, host="nw-node-zero", port=ports.MONGODB, **kwargs):
        super().__init__(
            host=host,
            port=port,
            tlsCAFile="/etc/pki/nw/trust/truststore.pem",
            tlsCertificateKeyFile="/etc/pki/nw/node/nodeadmin.pem",
            tlsAllowInvalidHostnames=True,
            authMechanism="MONGODB-X509",
            tls=True,
            **kwargs
        )
