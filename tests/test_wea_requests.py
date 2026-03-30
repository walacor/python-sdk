from unittest.mock import MagicMock, patch

import pytest

from pydantic import ValidationError

from walacor_sdk.wea.models.models import (
    BlockchainInfo,
    BlockInfoByHeight,
    BlockTransactionsDetailed,
    BlockTransactionsRangeData,
)
from walacor_sdk.wea.wea_service import WeaService


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return WeaService(mock_client)


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_blockchain_info_success(mock_logging, service):
    mock_response = {
        "success": True,
        "data": {
            "chainType": "z",
            "chainName": "y",
            "currentBlockHeight": 2237,
            "latestBlockHash": "x",
            "targetBlockTime": 10,
            "mineEmptyRounds": 6,
            "blockChainMempool": 0,
        },
    }

    service._get = MagicMock(return_value=mock_response)

    result = service.get_blockchain_info()

    assert isinstance(result, BlockchainInfo)
    assert result.chainType == "z"
    assert result.currentBlockHeight == 2237
    service._get.assert_called_once_with("blockchain/chain")
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.base.base_service.logger")
def test_get_blockchain_info_failure_flag(mock_logging, service):
    service._get = MagicMock(return_value={"success": False})

    result = service.get_blockchain_info()

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "get_blockchain_info" in rendered


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_blockchain_info_validation_error(mock_logging, service):
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service._get = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.wea.wea_service.BlockchainInfoResponse",
        side_effect=ValidationError.from_exception_data("BlockchainInfoResponse", []),
    ):
        result = service.get_blockchain_info()

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "BlockchainInfoResponse Validation Error" in mock_logging.error.call_args[0][0]
    )


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_block_info_by_height_success(mock_logging, service):
    height = 517
    mock_response = {
        "success": True,
        "data": {
            "hash": "x",
            "height": height,
            "time": 2,
            "txCount": 3,
            "txids": ["a", "b", "c"],
            "confirmations": 4,
            "previousBlockHash": "prev",
            "nextBlockHash": "next",
        },
    }

    service._get = MagicMock(return_value=mock_response)

    result = service.get_block_info_by_height(height)

    assert isinstance(result, BlockInfoByHeight)
    assert result.height == height
    assert result.txCount == 3
    service._get.assert_called_once_with("blockchain/block", params={"height": height})
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.base.base_service.logger")
def test_get_block_info_by_height_failure_flag(mock_logging, service):
    height = 517
    service._get = MagicMock(return_value={"success": False})

    result = service.get_block_info_by_height(height)

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "get_block_info_by_height" in rendered


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_block_info_by_height_validation_error(mock_logging, service):
    height = 517
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service._get = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.wea.wea_service.BlockInfoByHeightResponse",
        side_effect=ValidationError.from_exception_data(
            "BlockInfoByHeightResponse", []
        ),
    ):
        result = service.get_block_info_by_height(height)

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "BlockInfoByHeightResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_block_transaction_by_height_success(mock_logging, service):
    height = 517
    mock_response = {
        "success": True,
        "data": {
            "hash": "block_hash",
            "height": height,
            "txCount": 1,
            "transactions": [
                {
                    "hex": "abc",
                    "txid": "tx1",
                    "version": 1,
                    "locktime": 0,
                    "vin": [
                        {
                            "coinbase": "coinbase-data",
                            "sequence": 1,
                        }
                    ],
                    "vout": [
                        {
                            "value": 0,
                            "n": 0,
                            "scriptPubKey": {
                                "asm": "asm-data",
                                "hex": "hex-data",
                                "type": "nulldata",
                            },
                            "data": ["payload"],
                        }
                    ],
                    "blockhash": "block_hash",
                    "confirmations": 10,
                    "time": 123456,
                    "blocktime": 123456,
                }
            ],
        },
    }

    service._get = MagicMock(return_value=mock_response)

    result = service.get_block_transaction_by_height(height)

    assert isinstance(result, BlockTransactionsDetailed)
    assert result.height == height
    assert result.txCount == 1
    assert result.transactions[0].txid == "tx1"
    service._get.assert_called_once_with(
        "blockchain/block/transactions", params={"height": height}
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.base.base_service.logger")
def test_get_block_transaction_by_height_failure_flag(mock_logging, service):
    height = 517
    service._get = MagicMock(return_value={"success": False})

    result = service.get_block_transaction_by_height(height)

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "get_block_transaction_by_height" in rendered


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_block_transaction_by_height_validation_error(mock_logging, service):
    height = 517
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service._get = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.wea.wea_service.BlockTransactionsDetailedResponse",
        side_effect=ValidationError.from_exception_data(
            "BlockTransactionsDetailedResponse", []
        ),
    ):
        result = service.get_block_transaction_by_height(height)

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "BlockTransactionsDetailedResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )


# ------------------------------> GET BLOCK TRANSACTION BY RANGE


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_block_transaction_by_range_success(mock_logging, service):
    start_height = 500
    end_height = 600

    mock_response = {
        "success": True,
        "data": {
            "fromHeight": start_height,
            "toHeight": end_height,
            "blockCount": 2,
            "totalTransactions": 3,
            "blocks": [
                {
                    "hash": "block1",
                    "height": 500,
                    "txCount": 2,
                    "transactions": [
                        {
                            "TransId": "tx1",
                            "EID": "eid1",
                            "ETId": 10,
                        },
                        {
                            "TransId": "tx2",
                            "EID": "eid2",
                            "ETId": 11,
                        },
                    ],
                },
                {
                    "hash": "block2",
                    "height": 501,
                    "txCount": 1,
                    "transactions": [
                        {
                            "TransId": "tx3",
                            "EID": "eid3",
                            "ETId": 12,
                        }
                    ],
                },
            ],
        },
    }

    service._get = MagicMock(return_value=mock_response)

    result = service.get_block_transaction_by_range(start_height, end_height)

    assert isinstance(result, BlockTransactionsRangeData)
    assert result.fromHeight == start_height
    assert result.toHeight == end_height
    assert result.blockCount == 2
    assert result.totalTransactions == 3
    assert result.blocks[0].transactions[0].TransId == "tx1"
    service._get.assert_called_once_with(
        "blockchain/blocks/transactions/range",
        params={"fromHeight": start_height, "toHeight": end_height},
    )
    mock_logging.error.assert_not_called()


@patch("walacor_sdk.base.base_service.logger")
def test_get_block_transaction_by_range_failure_flag(mock_logging, service):
    start_height = 500
    end_height = 600
    service._get = MagicMock(return_value={"success": False})

    result = service.get_block_transaction_by_range(start_height, end_height)

    assert result is None
    mock_logging.error.assert_called_once()

    fmt, *args = mock_logging.error.call_args[0]
    rendered = fmt % tuple(args)
    assert "get_block_transaction_by_range" in rendered


@patch("walacor_sdk.wea.wea_service.logger")
def test_get_block_transaction_by_range_validation_error(mock_logging, service):
    start_height = 500
    end_height = 600
    bad_response = {"success": True, "data": {"invalid": "structure"}}
    service._get = MagicMock(return_value=bad_response)

    with patch(
        "walacor_sdk.wea.wea_service.BlockTransactionsRangeResponse",
        side_effect=ValidationError.from_exception_data(
            "BlockTransactionsRangeResponse", []
        ),
    ):
        result = service.get_block_transaction_by_range(start_height, end_height)

    assert result is None
    mock_logging.error.assert_called()
    assert (
        "BlockTransactionsRangeResponse Validation Error"
        in mock_logging.error.call_args[0][0]
    )
