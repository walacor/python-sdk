from walacor_sdk.base.walacor_service import WalacorService

service = WalacorService("http://44.203.135.11/api", "Admin", "GreenDoor99")
service.schema.getDataTypes()
