from dataclasses import dataclass, field
from pytezos import pytezos, ContractInterface
from pytezos.contract.result import OperationResult


DEFAULT_RESERVE = "tz1VYKnRgPyfZjdsnoVPyQrhBuhWHoP5QqxM"

ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"
CHARLIE_KEY = "edsk3G87qnDZhR74qYDFAC6nE17XxWkvPJtWpLw4vfeZ3otEWwwskV"
CHARLIE_PK = "tz1iYCR11SMJcpAH3egtDjZRQgLgKX6agU7s"
DEFAULT_BAKER = ALICE_PK
SMAK_TOKEN = None
SHELL = "http://localhost:8732"

_using_params = dict(shell=SHELL, key=ALICE_KEY)
send_conf = dict(min_confirmations=1)
bob_using_params = dict(shell=SHELL, key=BOB_KEY)
charlie_using_params = dict(shell=SHELL, key=CHARLIE_KEY)

pytezos = pytezos.using(**_using_params)
bob_pytezos = pytezos.using(**bob_using_params)
charlie_pytezos = pytezos.using(**charlie_using_params)


metadata = {
    "name": "",
    "version": "",
    "homepage": "",
    "authors": [""],
}
token_metadata = {
    "uri": "",
    "symbol": "",
    "decimals": "",
    "shouldPreferSymbol": "",
    "thumbnailUri": "",
}


@dataclass
class FA12Storage:
    admin: str = ALICE_PK
    tokens: dict = field(default_factory=lambda: {})
    allowances: dict = field(default_factory=lambda: {})
    metadata: dict = field(default_factory=lambda: {})
    paused: bool = False
    token_metadata: dict = field(default_factory=lambda: {})
    total_supply: int = 0


@dataclass
class FA2Storage:
    administrator: str = ALICE_PK
    all_tokens: int = 0
    ledger: dict = field(default_factory=lambda: {})
    metadata: dict = field(default_factory=lambda: {})
    operators: dict = field(default_factory=lambda: {})
    paused: bool = False
    token_metadata: dict = field(default_factory=lambda: {})


@dataclass
class MultisigStorage:
    admins: str = ALICE_PK
    authorized_contracts: str = ALICE_PK


@dataclass
class FactoryStorage:
    pairs: dict = field(default_factory=dict)
    pools: dict = field(default_factory=dict)
    default_smak_token_type: dict = field(
        default_factory=lambda: {"fa12": ALICE_PK})
    default_reserve: str = ALICE_PK
    default_sink: str = None
    counter: int = 0
    default_reward_rate: int = 300
    default_baker: str = DEFAULT_BAKER
    default_claim_limit: int = 100
    multisig: str = ALICE_PK
    default_user_rewards: int = 0


@dataclass
class DexStorage:
    self_is_updating_token_pool: bool = False
    token_pool_a: int = 0
    token_pool_b: int = 0
    token_type_a: dict = field(
        default_factory=lambda: {"fa12": ALICE_PK})
    token_type_b: dict = field(
        default_factory=lambda: {"fa12": ALICE_PK})
    token_type_smak: dict = field(
        default_factory=lambda: {"fa12": ALICE_PK})
    reserve: int = DEFAULT_RESERVE
    lqt_address: str = None
    lqt_total: int = 0
    history: dict = field(default_factory=lambda: {})
    user_investments: dict = field(default_factory=lambda: {})
    last_k: int = 0
    curve: dict = field(default_factory=lambda: {"product": None})
    manager: str = ALICE_PK
    freeze_baker: bool = False
    sink: str = ALICE_PK
    baker_rewards: str = None


@dataclass
class LqtStorage:
    tokens: dict = field(default_factory=lambda: {})
    allowances: dict = field(default_factory=lambda: {})
    admin: str = ALICE_PK
    total_supply: int = 0
    metadata: dict = field(default_factory=lambda: {})
    token_metadata: dict = field(default_factory=lambda: {})


@dataclass
class SinkStorage:
    token_type_smak: dict = field(default_factory=lambda: {"fa12": ALICE_PK})
    factory_address: str = ALICE_PK
    burn: dict = field(default_factory=lambda: {})
    reserve: dict = field(default_factory=lambda: {})
    reserve_address: str = ALICE_PK
    token_claim_limit: int = 25
    exchanges: dict = field(default_factory={})


class Env:
    def __init__(self, using_params=None):
        self.using_params = using_params or _using_params

    def deploy_fa2(self, init_storage: FA2Storage):
        with open("michelson/fa2.tz", encoding="UTF-8") as file:
            michelson = file.read()

        fa2 = ContractInterface.from_michelson(
            michelson).using(**self.using_params)

        storage = {
            "administrator": init_storage.administrator,
            "all_tokens": init_storage.all_tokens,
            "ledger": init_storage.ledger,
            "metadata": init_storage.metadata,
            "operators": init_storage.operators,
            "paused": init_storage.paused,
            "token_metadata": init_storage.token_metadata,
        }
        opg = fa2.originate(
            initial_storage=storage).send(**send_conf)
        fa2_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa2 = pytezos.using(**self.using_params).contract(fa2_addr)

        return fa2

    def deploy_fa12(self, init_storage: FA12Storage):
        with open("michelson/fa12.tz", encoding="UTF-8") as file:
            michelson = file.read()

        fa12 = ContractInterface.from_michelson(
            michelson).using(**self.using_params)

        storage = {
            "admin": init_storage.admin,
            "tokens": init_storage.tokens,
            "allowances": init_storage.allowances,
            "metadata": init_storage.metadata,
            "paused": init_storage.paused,
            "token_metadata": init_storage.token_metadata,
            "total_supply": init_storage.total_supply,
        }
        opg = fa12.originate(initial_storage=storage).send(**send_conf)
        fa12_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa12 = pytezos.using(**self.using_params).contract(fa12_addr)

        return fa12

    def deploy_multisig(self, init_storage: MultisigStorage):
        with open("michelson/multisig.tz", encoding="UTF-8") as file:
            source = file.read()
        multisig = ContractInterface.from_michelson(
            source).using(**self.using_params)
        storage = {
            "admins": {init_storage.admins},
            "n_calls": {},
            "threshold": 1,
            "duration": 3600,
            "authorized_contracts": {init_storage.authorized_contracts},
        }
        opg = multisig.originate(
            initial_storage=storage).send(**send_conf)
        multisig_address = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        multisig = pytezos.using(
            **self.using_params).contract(multisig_address)

        return multisig

    def deploy_liquidity_token(self, init_storage: LqtStorage):
        with open("michelson/lqt_fa12.tz", encoding="UTF-8") as file:
            source = file.read()

        liquidity_token = ContractInterface.from_michelson(
            source).using(**self.using_params)
        storage = {
            "tokens": init_storage.tokens,
            "allowances": init_storage.allowances,
            "admin": init_storage.admin,
            "total_supply": init_storage.total_supply,
            "metadata": init_storage.metadata,
            "token_metadata": init_storage.token_metadata,
        }
        opg = liquidity_token.originate(
            initial_storage=storage).send(**send_conf)
        liquidity_token_addr = OperationResult.from_operation_group(opg.opg_result)[
            0].originated_contracts[0]
        liquidity_token = pytezos.using(
            **self.using_params).contract(liquidity_token_addr)

        return liquidity_token

    def deploy_sink(self, init_storage: SinkStorage):
        with open("michelson/sink.tz", encoding="UTF-8") as file:
            source = file.read()

        sink = ContractInterface.from_michelson(source).using(**_using_params)
        storage = {
            "token_type_smak": init_storage.token_type_smak,
            "factory_address": init_storage.factory_address,
            "burn": init_storage.burn,
            "reserve": init_storage.reserve,
            "reserve_address": init_storage.reserve_address,
            "token_claim_limit": init_storage.token_claim_limit,
            "exchanges": init_storage.exchanges,
        }
        opg = sink.originate(
            initial_storage=storage).send(**send_conf)
        sink_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        sink = pytezos.using(**self.using_params).contract(sink_addr)

        return sink

    def deploy_factory(self, init_storage: FactoryStorage, admin: str):
        with open("michelson/factory.tz", encoding="UTF-8") as file:
            source = file.read()

        factory = ContractInterface.from_michelson(
            source).using(**self.using_params)

        print("deploy multisig")
        multisig = self.deploy_multisig(MultisigStorage(admins=admin))

        storage = {
            "pairs": init_storage.pairs,
            "pools": init_storage.pools,
            "default_smak_token_type": init_storage.default_smak_token_type,
            "default_reserve": init_storage.default_reserve,
            "default_sink": init_storage.default_sink,
            "default_reward_rate": init_storage.default_reward_rate,
            "counter": init_storage.counter,
            "default_baker": init_storage.default_baker,
            "default_claim_limit": init_storage.default_claim_limit,
            "multisig": multisig.address,
            "default_user_rewards": init_storage.default_user_rewards,
        }

        opg = factory.originate(
            initial_storage=storage).send(**send_conf)
        factory_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        factory = pytezos.using(**self.using_params).contract(factory_addr)
        # multisig_init_storage = MultisigStorage()
        # multisig_init_storage.authorized_contracts = factory_addr
        # multisig = self.deploy_multisig(multisig_init_storage)
        print("add factory to multisig")
        multisig.addAuthorizedContract(factory_addr).send(**send_conf)

        return factory

    def deploy_full_app(self, default_baker: str, admin: str):
        factory_init_storage = FactoryStorage()
        factory_init_storage.default_baker = default_baker
        print("deploy smak token")
        smak_token = self.deploy_fa12(
            FA12Storage(admin=admin)) if SMAK_TOKEN is None else SMAK_TOKEN
        factory_init_storage.default_smak_token_type = {
            "fa12": smak_token.address}
        print("deploy factory")
        factory = self.deploy_factory(factory_init_storage, admin)
        smak_token = pytezos.using(
            **self.using_params).contract(factory.storage["default_smak_token_type"]["fa12"]())
        print("launch sink")
        factory.launchSink().send(**send_conf)
        sink = pytezos.using(
            **self.using_params).contract(factory.storage["default_sink"]())
        multisig = pytezos.using(
            **self.using_params).contract(factory.storage["multisig"]())

        return factory, smak_token, sink, multisig
