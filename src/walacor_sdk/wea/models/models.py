from typing import Any

from pydantic import BaseModel


class BlockchainInfo(BaseModel):
    chainType: str
    chainName: str
    currentBlockHeight: int
    latestBlockHash: str
    targetBlockTime: int
    mineEmptyRounds: int
    blockChainMempool: int


class BlockInfoByHeight(BaseModel):
    hash: str
    height: int
    time: int
    txCount: int
    txids: list[str]
    confirmations: int
    previousBlockHash: str | None = None
    nextBlockHash: str | None = None


class TransactionSummary(BaseModel):
    TransId: str
    EId: str
    ETId: int


class BlockTransactionsInfo(BaseModel):
    hash: str
    height: int
    txCount: int
    transactions: list[TransactionSummary]


class ScriptSig(BaseModel):
    asm: str
    hex: str


class Vin(BaseModel):
    coinbase: str | None = None
    txid: str | None = None
    vout: int | None = None
    scriptSig: ScriptSig | None = None
    sequence: int


class ScriptPubKey(BaseModel):
    asm: str
    hex: str
    type: str
    reqSigs: int | None = None
    addresses: list[str] | None = None


class StreamItem(BaseModel):
    type: str
    name: str
    createtxid: str
    streamref: str
    publishers: list[str]
    keys: list[str]
    offchain: bool
    data: dict[str, Any]


class Vout(BaseModel):
    value: float
    n: int
    scriptPubKey: ScriptPubKey
    data: list[str] | None = None
    items: list[StreamItem] | None = None


class Transaction(BaseModel):
    hex: str
    txid: str
    version: int
    locktime: int
    vin: list[Vin]
    vout: list[Vout]
    blockhash: str
    confirmations: int
    time: int
    blocktime: int


class BlockTransactionsDetailed(BaseModel):
    hash: str
    height: int
    txCount: int
    transactions: list[Transaction]


class BlockTransactionSummary(BaseModel):
    hash: str
    height: int
    txCount: int
    transactions: list[TransactionSummary]


class BlockTransactionsRangeData(BaseModel):
    fromHeight: int
    toHeight: int
    blockCount: int
    totalTransactions: int
    blocks: list[BlockTransactionSummary]
