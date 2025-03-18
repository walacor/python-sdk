from walacor_sdk.base.model.base_response_model import BaseResponse
from walacor_sdk.schema.models.field_models import SchemaType


class SchemaResponse(BaseResponse[list[SchemaType]]):
    pass
