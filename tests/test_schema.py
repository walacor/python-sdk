from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.schema.models.models import (
    AutoGenField,
    CreateFieldRequest,
    CreateSchemaDefinition,
    IndexEntry,
    IntegerField,
    SchemaDetail,
    SchemaEntry,
    SchemaItem,
    SchemaMetadata,
    SchemaQueryList,
    SchemaSummary,
    SchemaVersionEntry,
)
from walacor_sdk.schema.models.schema_request import (
    CreateSchemaRequest,
    SchemaQueryListRequest,
)
from walacor_sdk.schema.models.schema_response import (
    CreateSchemaResponse,
    GetSchemaDetailResponse,
    GetSchemaListResponse,
    SchemaQueryListResponse,
    SchemaResponse,
)
from walacor_sdk.schema.schema_service import SchemaService
from walacor_sdk.utils.enums import SystemEnvelopeType


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return SchemaService(mock_client)


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_data_types_success(mock_logging, service):
    """Test successful parsing of get_data_types with valid response."""
    mock_response = SchemaResponse(
        success=True,
        message="Fetched",
        data=[IntegerField(Name="INTEGER", DefaultValue=0, MinValue=0, MaxValue=100)],
    )
    service._get = MagicMock(return_value=mock_response.model_dump())

    result = service.get_data_types()

    assert len(result) == 1
    assert isinstance(result[0], IntegerField)
    assert result[0].Name == "INTEGER"
    mock_logging.info.assert_called_with("Fetching data types...")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_data_types_failure_flag(mock_logging, service):
    """Test get_data_types returns empty list when success flag is False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_data_types()

    assert result == []
    mock_logging.error.assert_called_with("Failed to fetch data")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_data_types_validation_error(mock_logging, service):
    """Test get_data_types handles ValidationError and logs it."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaResponse",
        side_effect=ValidationError.from_exception_data("SchemaResponse", []),
    ):
        result = service.get_data_types()

        assert result == []
        mock_logging.error.assert_called()
        assert "Schema Validation Error" in mock_logging.error.call_args[0][0]


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_platform_auto_generation_fields_success(mock_logging, service):
    """Test successful parsing of get_platform_auto_generation_fields with valid response."""
    mock_response = {
        "success": True,
        "data": {
            "FieldA": {
                "FieldName": "FieldA",
                "DataType": "TEXT",
                "Required": True,
                "SystemGenerated": False,
            }
        },
    }
    service._get = MagicMock(return_value=mock_response)

    result = service.get_platform_auto_generation_fields()

    assert isinstance(result, dict)
    assert "FieldA" in result
    assert isinstance(result["FieldA"], AutoGenField)
    assert result["FieldA"].FieldName == "FieldA"
    mock_logging.info.assert_called_with("Fetching platform auto-generation fields...")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_platform_auto_generation_fields_failure_flag(mock_logging, service):
    """Test get_platform_auto_generation_fields returns empty dict when success flag is False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_platform_auto_generation_fields()

    assert result == {}
    mock_logging.error.assert_called_with(
        "Failed to fetch platform auto-generation fields"
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_platform_auto_generation_fields_validation_error(mock_logging, service):
    """Test get_platform_auto_generation_fields handles ValidationError and logs it."""
    service._get = MagicMock(return_value={"success": True, "data": {"Invalid": {}}})

    with patch(
        "walacor_sdk.schema.models.schema_response.AutoGenFieldsResponse",
        side_effect=ValidationError.from_exception_data("AutoGenFieldsResponse", []),
    ):
        result = service.get_platform_auto_generation_fields()

        assert result == {}
        mock_logging.error.assert_called()
        assert "AutoGenFields Validation Error" in mock_logging.error.call_args[0][0]


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_list_with_latest_version_success(mock_logging, service):
    """Test method returns empty list and logs error when success is False."""
    mock_response = {
        "success": True,
        "data": [{"ETId": 1, "TableName": "TestTable", "SV": 1}],
    }

    service._get = MagicMock(return_value=mock_response)

    result = service.get_list_with_latest_version()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], SchemaEntry)
    assert result[0].ETId == 1
    assert result[0].TableName == "TestTable"
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_list_with_latest_version_failure_flag(mock_logging, service):
    """Test method returns empty list and logs error when success is False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_list_with_latest_version()

    assert result == []
    mock_logging.error.assert_called_with("Failed to fetch latest schema versions")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_list_with_latest_version_validation_error(mock_logging, service):
    """Test method returns empty list and logs ValidationError on invalid response."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaListResponse",
        side_effect=ValidationError.from_exception_data("SchemaListResponse", []),
    ):
        result = service.get_list_with_latest_version()

        assert result == []
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_versions_success(mock_logging, service):
    """Test successful parsing of schema versions list."""
    mock_response = {"success": True, "data": [{"ETId": 101, "versions": [1, 2, 3]}]}
    service._get = MagicMock(return_value=mock_response)

    result = service.get_versions()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], SchemaVersionEntry)
    assert result[0].ETId == 101
    assert result[0].versions == [1, 2, 3]
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_versions_failure_flag_returns_empty_list(mock_logging, service):
    """Test that method returns an empty list if API returns success=False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_versions()

    assert result == []
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_versions_validation_error(mock_logging, service):
    """Test that method logs ValidationError and returns empty list."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaVersionsResponse",
        side_effect=ValidationError.from_exception_data("SchemaVersionsResponse", []),
    ):
        result = service.get_versions()

        assert result == []
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_versions_for_ETId(mock_logging, service):
    """Test get_versions_for_ETId returns list of integers on valid response."""
    mock_response = {"success": True, "data": [1, 2, 3]}

    service._get = MagicMock(return_value=mock_response)

    result = service.get_versions_for_ETId(ETId=4)

    assert result == [1, 2, 3]
    service._get.assert_called_with("schemas/envelopeTypes/4/versions")
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_versions_for_etid_failure_flag(mock_logging, service):
    """Test get_versions_for_ETId returns empty list when response is unsuccessful."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_versions_for_ETId(ETId=42)

    assert result == []
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_versions_for_etid_validation_error(mock_logging, service):
    """Test get_versions_for_ETId returns empty list on ValidationError and logs it."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaListResponse",
        side_effect=ValidationError.from_exception_data(
            "SchemaListVersionsResponse", []
        ),
    ):
        result = service.get_versions_for_ETId(ETId=42)

        assert result == []
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_with_int_etid_success(mock_logging, service):
    """Test get_indexes handles integer ETId and parses IndexEntry list correctly."""
    mock_response = {
        "success": True,
        "data": [{"v": 1, "key": {"_id": 100}, "name": "IndexA", "ns": "ns.table"}],
    }
    service._get = MagicMock(return_value=mock_response)

    result = service.get_indexes(ETId=15)

    assert isinstance(result, list)
    assert isinstance(result[0], IndexEntry)
    assert result[0].name == "IndexA"
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/15/indexes", {"ETId": "15"}
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_with_string_etid_success(mock_logging, service):
    """Test get_indexes handles string ETId and returns parsed IndexEntry list."""
    mock_response = {
        "success": True,
        "data": [{"v": 2, "key": {"_id": 101}, "name": "IndexB", "ns": "db.index"}],
    }
    service._get = MagicMock(return_value=mock_response)

    result = service.get_indexes(ETId="15")

    assert isinstance(result, list)
    assert isinstance(result[0], IndexEntry)
    assert result[0].name == "IndexB"
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/15/indexes", {"ETId": "15"}
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_with_enum_etid_success(mock_logging, service):
    """Test get_indexes handles SystemEnvelopeType enum and returns parsed IndexEntry list."""
    mock_response = {
        "success": True,
        "data": [
            {"v": 3, "key": {"_id": 200}, "name": "EnumIndex", "ns": "enum.table"}
        ],
    }
    service._get = MagicMock(return_value=mock_response)

    result = service.get_indexes(ETId=SystemEnvelopeType.Schema)

    assert isinstance(result, list)
    assert isinstance(result[0], IndexEntry)
    assert result[0].name == "EnumIndex"
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/15/indexes",
        {"ETId": str(SystemEnvelopeType.Schema.value)},
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_failure_flag(mock_logging, service):
    """Test get_indexes returns empty list and logs validation error on invalid response structure."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_indexes(9)

    assert result == []
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/15/indexes", {"ETId": "9"}
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_schema_index_response_model_validation_error(mock_logging, service):
    """Test SchemaIndexResponse model raises ValidationError when 'data' is missing."""
    service._get = MagicMock(return_value={"success": True})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaIndexResponse",
        side_effect=ValidationError.from_exception_data("SchemaIndexResponse", []),
    ):
        result = service.get_indexes(ETId=99)

        assert result == []
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_with_table_name_success(mock_logging, service):
    mock_response = {
        "success": True,
        "data": [{"v": 1, "key": {"_id": 111}, "name": "IndexB", "ns": "db.index"}],
    }
    service._get = MagicMock(return_value=mock_response)

    result = service.get_indexes_by_table_name(tableName="TestTable")

    assert isinstance(result, list)
    assert isinstance(result[0], IndexEntry)
    assert result[0].name == "IndexB"
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/15/indexesByTableName?tableName=TestTable"
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_wit_table_name_failure_flag(mock_logging, service):
    service._get = MagicMock(return_value={"success": False})

    result = service.get_indexes_by_table_name("TestTable")

    assert result == []
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/15/indexesByTableName?tableName=TestTable"
    )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_indexes_by_table_name_validation_error(mock_logging, service):
    """Test get_indexes_by_table_name handles ValidationError and logs it."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.IndexesByTableNameResponse",
        side_effect=ValidationError.from_exception_data(
            "IndexesByTableNameResponse", []
        ),
    ):
        result = service.get_indexes_by_table_name("TestTable")

        assert result == []
        service._get.assert_called_once_with(
            "schemas/envelopeTypes/15/indexesByTableName?tableName=TestTable"
        )
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_create_schema_success(mock_logging, service):
    """Test create_schema returns parsed SchemaMetadata on valid response."""
    request = CreateSchemaRequest(
        ETId=50,
        SV=1,
        Schema=CreateSchemaDefinition(
            ETId=123456,
            TableName="MyTable",
            Family="MyFamily",
            DoSummary=False,
            Fields=[
                CreateFieldRequest(FieldName="field1", DataType="TEXT", Required=True)
            ],
            Indexes=[],
        ),
    )

    mock_response = CreateSchemaResponse(
        success=True,
        message="ok",
        data=SchemaMetadata(
            EId="eid123",
            ETId=123456,
            SV=1,
            ES=1,
            CreatedAt=123456,
            UpdatedAt=123456,
            UID=["user1"],
        ),
    )

    service._post = MagicMock(return_value=mock_response.model_dump())

    result = service.create_schema(request)

    assert isinstance(result, SchemaMetadata)
    assert result.EId == "eid123"
    service._post.assert_called_once_with(
        "schemas/", json=request.model_dump(), headers={"ETId": "50", "SV": "1"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_create_schema_validation_error(mock_logging, service):
    """Test create_schema returns None and logs ValidationError on bad response."""
    request = CreateSchemaRequest(
        ETId=50,
        SV=1,
        Schema=CreateSchemaDefinition(
            ETId=12345,
            TableName="MyTable",
            Family="MyFamily",
            DoSummary=False,
            Fields=[
                CreateFieldRequest(FieldName="field1", DataType="TEXT", Required=True)
            ],
            Indexes=[],
        ),
    )

    invalid_response = {"success": True, "data": {}}
    service.post = MagicMock(return_value=invalid_response)
    with patch(
        "walacor_sdk.schema.models.schema_response.CreateSchemaResponse",
        side_effect=ValidationError.from_exception_data("CreateSchemaResponse", []),
    ):
        result = service.create_schema(request)

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_schema_details_with_etid_success(mock_logging, service):
    """Test get_schema_details_with_ETId returns SchemaDetail on valid response."""
    mock_response = GetSchemaDetailResponse(
        success=True,
        message="ok",
        data=SchemaDetail(
            _id="abc123",
            ETId=50,
            TableName="MyTable",
            Family="MyFamily",
            DoSummary=False,
            Fields=[],
            Indexes=[],
            DbTableName="tbl",
            DbHistoryTableName="tbl_hist",
            SV=1,
            LastModifiedBy="user",
            UID="uid123",
            ORGId="org1",
            SL="sl",
            HashSign="hash",
            HS="hs",
            EId="eid",
            UpdatedAt=123456,
            IsDeleted=False,
            CreatedAt=123456,
        ),
    )

    service._get = MagicMock(return_value=mock_response.model_dump(by_alias=True))

    result = service.get_schema_details_with_ETId(ETId=50)

    assert isinstance(result, SchemaDetail)
    assert result.ETId == 50
    assert result.TableName == "MyTable"
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/50/details", headers={"ETId": "50"}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_schema_details_with_etid_failure_flag(mock_logging, service):
    """Test get_schema_details_with_ETId returns None when success=False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_schema_details_with_ETId(ETId=50)

    assert result is None
    service._get.assert_called_once_with(
        "schemas/envelopeTypes/50/details", headers={"ETId": "50"}
    )
    mock_logging.error.assert_called_with("Failed to fetch schema details")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_schema_details_with_etid_validation_error(mock_logging, service):
    """Test get_schema_details_with_ETId returns None and logs error on invalid response."""
    service._get = MagicMock(return_value={"success": True, "data": {}})

    with patch(
        "walacor_sdk.schema.models.schema_response.GetSchemaDetailResponse",
        side_effect=ValidationError.from_exception_data("GetSchemaDetailResponse", []),
    ):
        result = service.get_schema_details_with_ETId(ETId=42)

        assert result is None
        service._get.assert_called_once_with(
            "schemas/envelopeTypes/42/details", headers={"ETId": "42"}
        )
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )

        patch("walacor_sdk.schema.schema_service.logging")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_envelope_types_success(mock_logging, service):
    """Test get_envelope_types returns list of integers on valid response."""
    mock_response = {"success": True, "data": [100, 200, 300]}
    service._get = MagicMock(return_value=mock_response)

    result = service.get_envelope_types()

    assert result == [100, 200, 300]
    service._get.assert_called_once_with("schemas/envelopeTypes")
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_envelope_types_failure_flag(mock_logging, service):
    """Test get_envelope_types returns None and logs error when success is False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_envelope_types()

    assert result is None
    service._get.assert_called_once_with("schemas/envelopeTypes")
    mock_logging.error.assert_called_with("Failed to fetch schema details")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_envelope_types_validation_error(mock_logging, service):
    """Test get_envelope_types returns None on ValidationError and logs it."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.GetEnvelopeTypesResponse",
        side_effect=ValidationError.from_exception_data("GetEnvelopeTypesResponse", []),
    ):
        result = service.get_envelope_types()

        assert result is None
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_details_by_id_success(mock_logging, service):
    """Test get_details_by_id returns SchemaDetail on valid response."""
    mock_response = GetSchemaDetailResponse(
        success=True,
        message="ok",
        data=SchemaDetail(
            _id="abc123",
            ETId=50,
            TableName="MyTable",
            Family="MyFamily",
            DoSummary=False,
            Fields=[],
            Indexes=[],
            DbTableName="tbl",
            DbHistoryTableName="tbl_hist",
            SV=1,
            LastModifiedBy="user",
            UID="uid123",
            ORGId="org1",
            SL="sl",
            HashSign="hash",
            HS="hs",
            EId="eid",
            UpdatedAt=123456,
            IsDeleted=False,
            CreatedAt=123456,
        ),
    )

    service._get = MagicMock(return_value=mock_response.model_dump(by_alias=True))

    result = service.get_details_by_id("abc123")

    assert isinstance(result, SchemaDetail)
    assert result.ETId == 50
    assert result.TableName == "MyTable"
    service._get.assert_called_once_with("schemas/abc123")
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_details_by_id_failure_flag(mock_logging, service):
    """Test get_details_by_id returns None and logs error when success is False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_details_by_id("invalid_id")

    assert result is None
    service._get.assert_called_once_with("schemas/invalid_id")
    mock_logging.error.assert_called_with("Failed to fetch schema details")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_details_by_id_validation_error(mock_logging, service):
    """Test get_details_by_id returns None and logs ValidationError on invalid response."""
    service._get = MagicMock(return_value={"success": True, "data": {}})

    with patch(
        "walacor_sdk.schema.models.schema_response.GetSchemaDetailResponse",
        side_effect=ValidationError.from_exception_data("GetSchemaDetailResponse", []),
    ):
        result = service.get_details_by_id("bad_schema_id")

        assert result is None
        service._get.assert_called_once_with("schemas/bad_schema_id")
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_list_schema_items_success(mock_logging, service):
    """Test get_list_schema_items returns list of SchemaItem on valid response."""
    mock_response = GetSchemaListResponse(
        success=True,
        message="ok",
        data=[
            SchemaItem(
                _id="618b8002347bcd002179b482",
                ORGId="5dadbc17d52c4ef58fc97f1aaf81bdab1",
                ORGName="Default",
                EId="a04e8bcb-7270-4837-b56c-4980892d6eec",
                ETId=2,
                DV=1,
                TableName="setting",
                DbTableName="2_setting",
                DbHistoryTableName="2_histories",
                Family="system",
                DoSummary=True,
                Description="Setting for Organization",
                LastModifiedBy="bbecdf99-f3e4-44d3-b81b-679d845dc993",
                CreatedAt=1636532225380,
                UpdatedAt=1636532225380,
            )
        ],
    )

    service._get = MagicMock(return_value=mock_response.model_dump(by_alias=True))

    result = service.get_list_schema_items()

    assert isinstance(result, list)
    assert isinstance(result[0], SchemaItem)
    assert result[0].ORGId == "5dadbc17d52c4ef58fc97f1aaf81bdab1"
    service._get.assert_called_once_with("schemas")
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_list_schema_items_failure_flag(mock_logging, service):
    """Test get_list_schema_items returns None and logs error when success is False."""
    service._get = MagicMock(return_value={"success": False})

    result = service.get_list_schema_items()

    assert result is None
    service._get.assert_called_once_with("schemas")
    mock_logging.error.assert_called_with("Failed to fetch schema details")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_list_schema_items_validation_error(mock_logging, service):
    """Test get_list_schema_items logs ValidationError and returns None on malformed response."""
    service._get = MagicMock(return_value={"success": True, "data": [{}]})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaListResponse",
        side_effect=ValidationError.from_exception_data("SchemaListResponse", []),
    ):
        result = service.get_list_schema_items()

        assert result is None
        service._get.assert_called_once_with("schemas")
        mock_logging.error.assert_called()
        assert (
            "SchemaListResponse Validation Error" in mock_logging.error.call_args[0][0]
        )


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_schema_query_schema_items_success(mock_logging, service):
    """Test get_schema_query_schema_items handles full query with pagination, ordering, and dates."""
    query = SchemaQueryListRequest(
        page=1,
        pageSize=10,
        order="desc",
        orderBy="Family",
        startDate="2024-10-01T14:10:17.272Z",
        endDate="2025-10-12T14:10:17.272Z",
    )

    mock_response = SchemaQueryListResponse(
        success=True,
        message="Fetched successfully",
        total=1,
        data=[
            SchemaSummary(
                schema="schemaX",
                UID="uid123",
                ETId=102,
                createdDate=1739396098164,
                Family="system",
                SV=1,
                numberOfFields=5,
            )
        ],
    )

    service._get = MagicMock(return_value=mock_response.model_dump(by_alias=True))

    result = service.get_schema_query_schema_items(query)

    assert isinstance(result, SchemaQueryList)
    assert isinstance(result.data, list)
    assert isinstance(result.data[0], SchemaSummary)
    assert result.data[0].Family == "system"
    assert result.total == 1
    service._get.assert_called_once_with(
        "schemas/schemaList", params=query.model_dump(exclude_none=True)
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_schema_query_schema_items_failure_flag(mock_logging, service):
    """Test get_schema_query_schema_items returns None and logs error when success is False."""
    service._get = MagicMock(return_value={"success": False, "data": [{}]})

    queryParams = SchemaQueryListRequest(
        page=1,
        pageSize=10,
        order="desc",
        orderBy="Family",
        startDate="2024-10-01T14:10:17.272Z",
        endDate="2025-10-12T14:10:17.272Z",
    )

    result = service.get_schema_query_schema_items(queryParams)

    assert result is None
    service._get.assert_called_once_with(
        "schemas/schemaList", params=queryParams.model_dump(exclude_none=True)
    )
    mock_logging.error.assert_called_with("Failed to fetch schema details")


@patch("walacor_sdk.schema.schema_service.logging")
def test_get_schema_query_schema_items_validation_error(mock_logging, service):
    """Test get_schema_query_schema_items returns None and logs ValidationError on invalid response."""

    queryParams = SchemaQueryListRequest(
        page=1,
        pageSize=10,
        order="desc",
        orderBy="Family",
        startDate="2024-10-01T14:10:17.272Z",
        endDate="2025-10-12T14:10:17.272Z",
    )

    service._get = MagicMock(return_value={"success": True, "data": [{}], "total": 1})

    with patch(
        "walacor_sdk.schema.models.schema_response.SchemaQueryListResponse",
        side_effect=ValidationError.from_exception_data("SchemaQueryListResponse", []),
    ):
        result = service.get_schema_query_schema_items(queryParams)

        assert result is None
        service._get.assert_called_once_with(
            "schemas/schemaList", params=queryParams.model_dump(exclude_none=True)
        )
        mock_logging.error.assert_called()
        assert "SchemaQueryList Validation Error" in mock_logging.error.call_args[0][0]
