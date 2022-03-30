import unittest
from dataclasses import dataclass, field
from decimal import Decimal
from pytezos import pytezos, ContractInterface
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult


DEFAULT_RESERVE = "tz1VYKnRgPyfZjdsnoVPyQrhBuhWHoP5QqxM"
ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"
CHARLIE_KEY = "edsk3G87qnDZhR74qYDFAC6nE17XxWkvPJtWpLw4vfeZ3otEWwwskV"
CHARLIE_PK = "tz1iYCR11SMJcpAH3egtDjZRQgLgKX6agU7s"
SHELL = "http://localhost:20000"

# hangzhounet
# DEFAULT_BAKER = "tz1MeT8NACB8Q4uV9dPQ3YxXBmYgapbxQxQ5"

# sandbox
DEFAULT_BAKER = ALICE_PK

_using_params = dict(shell=SHELL, key=ALICE_KEY)
bob_using_params = dict(shell=SHELL, key=BOB_KEY)
charlie_using_params = dict(shell=SHELL, key=CHARLIE_KEY)

pytezos = pytezos.using(**_using_params)
bob_pytezos = pytezos.using(**bob_using_params)
charlie_pytezos = pytezos.using(**charlie_using_params)

send_conf = dict(min_confirmations=1)

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
    default_lp_metadata: dict = field(default_factory=dict)
    default_lp_allowances: dict = field(default_factory=dict)
    default_lp_token_metadata: dict = field(default_factory=dict)
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
        with open("FA2.tz", encoding="UTF-8") as file:
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
        opg = fa2.originate(initial_storage=storage).send(**send_conf)
        fa2_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa2 = pytezos.using(**self.using_params).contract(fa2_addr)

        return fa2

    def deploy_fa12(self, init_storage: FA12Storage):
        with open("../michelson/fa12.tz", encoding="UTF-8") as file:
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

    def deploy_multisig(self, init_storage: MultisigStorage()):
        with open("../michelson/multisig.tz", encoding="UTF-8") as file:
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
        opg = multisig.originate(initial_storage=storage).send(**send_conf)
        multisig_address = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        multisig = pytezos.using(
            **self.using_params).contract(multisig_address)

        return multisig

    def deploy_liquidity_token(self, init_storage: LqtStorage):
        with open("../michelson/lqt_fa12.tz", encoding="UTF-8") as file:
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
        with open("../michelson/sink.tz", encoding="UTF-8") as file:
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
        opg = sink.originate(initial_storage=storage).send(**send_conf)
        sink_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        sink = pytezos.using(**self.using_params).contract(sink_addr)

        return sink

    def deploy_factory(self, init_storage: FactoryStorage, **kwargs):
        with open("../michelson/factory.tz", encoding="UTF-8") as file:
            source = file.read()

        factory = ContractInterface.from_michelson(
            source).using(**self.using_params)

        storage = {
            "pairs": init_storage.pairs,
            "pools": init_storage.pools,
            "default_smak_token_type": init_storage.default_smak_token_type,
            "default_reserve": init_storage.default_reserve,
            "default_sink": init_storage.default_sink,
            "default_lp_metadata": init_storage.default_lp_metadata,
            "default_lp_allowances": init_storage.default_lp_allowances,
            "default_lp_token_metadata": init_storage.default_lp_token_metadata,
            "default_reward_rate": init_storage.default_reward_rate,
            "counter": init_storage.counter,
            "default_baker": init_storage.default_baker,
            "default_claim_limit": init_storage.default_claim_limit,
            "multisig": init_storage.multisig,
            "default_user_rewards": init_storage.default_user_rewards,
        }

        opg = factory.originate(initial_storage=storage).send(**send_conf)
        factory_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        factory = pytezos.using(**self.using_params).contract(factory_addr)
        multisig_init_storage = MultisigStorage()
        multisig_init_storage.authorized_contracts = factory_addr
        multisig = self.deploy_multisig(multisig_init_storage)
        factory.updateMultisig(multisig.address).send(**send_conf)

        return factory

    def deploy_full_app(self):
        factory_init_storage = FactoryStorage()
        smak_token = self.deploy_fa12(FA12Storage())
        factory_init_storage.default_smak_token_type = {
            "fa12": smak_token.address}
        factory = self.deploy_factory(factory_init_storage)
        smak_token = pytezos.using(
            **self.using_params).contract(factory.storage["default_smak_token_type"]["fa12"]())
        factory.launchSink().send(**send_conf)
        sink = pytezos.using(
            **self.using_params).contract(factory.storage["default_sink"]())
        multisig = pytezos.using(
            **self.using_params).contract(factory.storage["multisig"]())

        return factory, smak_token, sink, multisig

    def deploy_app_with_all_pairs(self):
        factory, smak_token, sink, multisig = self.deploy_full_app()
        pairs = []
        # pair0 fa12 -> fa12
        pair0_token_a = self.deploy_fa12(FA12Storage())
        pair0_token_b = self.deploy_fa12(FA12Storage())
        pair0_token_a_type = {"fa12": pair0_token_a.address}
        pair0_token_b_type = {"fa12": pair0_token_b.address}
        pairs.append({"token_a": pair0_token_a_type,
                      "token_a_address": pair0_token_a.address,
                      "token_b_address": pair0_token_b.address,
                      "token_b": pair0_token_b_type})
        # pair1 fa12 -> fa2
        pair1_token_a = self.deploy_fa12(FA12Storage())
        pair1_token_b = self.deploy_fa2(FA2Storage())
        pair1_token_a_type = {"fa12": pair1_token_a.address}
        pair1_token_b_type = {"fa2": (pair1_token_b.address, 0)}
        pairs.append({"token_a": pair1_token_a_type,
                      "token_a_address": pair1_token_a.address,
                      "token_b_address": pair1_token_b.address,
                      "token_b": pair1_token_b_type})
        # pair2 fa12 -> XTZ
        pair2_token_a = self.deploy_fa12(FA12Storage())
        pair2_token_a_type = {"fa12": pair2_token_a.address}
        pair2_token_b_type = {"xtz": None}
        pairs.append({"token_a": pair2_token_a_type,
                      "token_a_address": pair2_token_a.address,
                      "token_b_address": None,
                      "token_b": pair2_token_b_type})
        # pair3 fa2 -> fa12
        pair3_token_a = self.deploy_fa2(FA2Storage())
        pair3_token_b = self.deploy_fa12(FA12Storage())
        pair3_token_a_type = {"fa2": (pair3_token_a.address, 0)}
        pair3_token_b_type = {"fa12": pair3_token_b.address}
        pairs.append({"token_a": pair3_token_a_type,
                      "token_a_address": pair3_token_a.address,
                      "token_b_address": pair3_token_b.address,
                      "token_b": pair3_token_b_type})
        # pair4 fa2 -> fa2
        pair4_token_a = self.deploy_fa2(FA2Storage())
        pair4_token_b = self.deploy_fa2(FA2Storage())
        pair4_token_a_type = {"fa2": (pair4_token_a.address, 0)}
        pair4_token_b_type = {"fa2": (pair4_token_b.address, 0)}
        pairs.append({"token_a": pair4_token_a_type,
                      "token_a_address": pair4_token_a.address,
                      "token_b_address": pair4_token_b.address,
                      "token_b": pair4_token_b_type})
        # pair5 fa2 -> XTZ
        pair5_token_a = self.deploy_fa2(FA2Storage())
        pair5_token_a_type = {"fa2": (pair5_token_a.address, 0)}
        pair5_token_b_type = {"xtz": None}
        pairs.append({"token_a": pair5_token_a_type,
                      "token_a_address": pair5_token_a.address,
                      "token_b_address": None,
                      "token_b": pair5_token_b_type})
        # pair6 XTZ -> fa12
        pair6_token_b = self.deploy_fa12(FA12Storage())
        pair6_token_a_type = {"xtz": None}
        pair6_token_b_type = {"fa12": pair6_token_b.address}
        pairs.append({"token_a": pair6_token_a_type,
                      "token_a_address": None,
                      "token_b_address": pair6_token_b.address,
                      "token_b": pair6_token_b_type})
        # pair7 XTZ -> fa2
        pair7_token_b = self.deploy_fa2(FA2Storage())
        pair7_token_a_type = {"xtz": None}
        pair7_token_b_type = {"fa2": (pair7_token_b.address, 0)}
        pairs.append({"token_a": pair7_token_a_type,
                      "token_a_address": None,
                      "token_b_address": pair7_token_b.address,
                      "token_b": pair7_token_b_type})
        # pair8 fa12 -> SMAK
        pair8_token_a = self.deploy_fa12(FA12Storage())
        pair8_token_a_type = {"fa12": pair8_token_a.address}
        pair8_token_b_type = {"fa12": smak_token.address}
        pairs.append({"token_a": pair8_token_a_type,
                      "token_a_address": pair8_token_a.address,
                      "token_b_address": smak_token.address,
                      "token_b": pair8_token_b_type})
        # pair9 fa2 -> SMAK
        pair9_token_a = self.deploy_fa2(FA2Storage())
        pair9_token_a_type = {"fa2": (pair9_token_a.address, 0)}
        pair9_token_b_type = {"fa12": smak_token.address}
        pairs.append({"token_a": pair9_token_a_type,
                      "token_a_address": pair9_token_a.address,
                      "token_b_address": smak_token.address,
                      "token_b": pair9_token_b_type})
        # pair10 XTZ -> SMAK
        pair10_token_a_type = {"xtz": None}
        pair10_token_b_type = {"fa12": smak_token.address}
        pairs.append({"token_a": pair10_token_a_type,
                      "token_a_address": None,
                      "token_b_address": smak_token.address,
                     "token_b": pair10_token_b_type})
        # pair11 SMAK -> fa12
        pair11_token_a_type = {"fa12": smak_token.address}
        pair11_token_b = self.deploy_fa12(FA12Storage())
        pair11_token_b_type = {"fa12": pair11_token_b.address}
        pairs.append({"token_a": pair11_token_a_type,
                      "token_a_address": smak_token.address,
                      "token_b_address": pair11_token_b.address,
                     "token_b": pair11_token_b_type})
        # pair12 SMAK -> fa2
        pair12_token_a_type = {"fa12": smak_token.address}
        pair12_token_b = self.deploy_fa2(FA2Storage())
        pair12_token_b_type = {"fa2": (pair12_token_b.address, 0)}
        pairs.append({"token_a": pair12_token_a_type,
                      "token_a_address": smak_token.address,
                      "token_b_address": pair12_token_b.address,
                     "token_b": pair12_token_b_type})

        for pair in pairs:
            token_a = pair["token_a"]
            token_a_address = pair["token_a_address"]
            token_b = pair["token_b"]
            token_b_address = pair["token_b_address"]
            if "fa12" in token_a:
                pytezos.contract(token_a_address).mint(
                    {"address": ALICE_PK, "value": 10 ** 10}).send(**send_conf)
                pytezos.contract(token_a_address).approve({"spender": factory.address,
                                                           "value": 10 ** 10}).send(**send_conf)
            elif "fa2" in token_a:
                pytezos.contract(token_a_address).mint({"address": ALICE_PK, "amount": 10 ** 10,
                                                        "metadata": {}, "token_id": 0}).send(**send_conf)
                pytezos.contract(token_a_address).update_operators([{"add_operator": {
                    "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            if "fa12" in token_b:
                pytezos.contract(token_b_address).mint(
                    {"address": ALICE_PK, "value": 10 ** 10}).send(**send_conf)
                pytezos.contract(token_b_address).approve({"spender": factory.address,
                                                           "value": 10 ** 10}).send(**send_conf)
            elif "fa2" in token_b:
                pytezos.contract(token_b_address).mint({"address": ALICE_PK, "amount": 10 ** 10,
                                                        "metadata": {}, "token_id": 0}).send(**send_conf)
                pytezos.contract(token_b_address).update_operators([{"add_operator": {
                    "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)

            token_amount_a = {"mutez": 10 ** 10} if token_a == {
                "xtz": None} else {"amount": 10 ** 10}
            token_amount_b = {"mutez": 10 ** 10} if token_b == {
                "xtz": None} else {"amount": 10 ** 10}

            amount_to_send = 10 ** 10 if token_a == {
                "xtz": None} or token_b == {"xtz": None} else 0

            launch_exchange_params = {
                "token_type_a": token_a,
                "token_type_b": token_b,
                "token_amount_a": token_amount_a,
                "token_amount_b": token_amount_b,
                "curve": {"flat": None},
                "metadata": metadata,
                "token_metadata": token_metadata
            }

            factory.launchExchange(launch_exchange_params).with_amount(
                amount_to_send).send(**send_conf)

        return factory, smak_token, sink


class TestEnv(unittest.TestCase):
    def test_deploy_fa2(self):
        init_storage = FA2Storage()
        fa2 = Env().deploy_fa2(init_storage)

        self.assertEqual(fa2.storage["administrator"](), ALICE_PK)

    def test_deploy_fa12(self):
        init_storage = FA12Storage(ALICE_PK)
        fa12 = Env().deploy_fa12(init_storage)

        self.assertEqual(fa12.storage["admin"](), ALICE_PK)

    def test_deploy_factory(self):
        init_storage = FactoryStorage()
        factory = Env().deploy_factory(init_storage)

    def test_deploy_liquidity_token(self):
        init_storage = LqtStorage()
        lqt = Env().deploy_liquidity_token(init_storage)

    def test_deploy_full_app(self):
        factory, smak_token, sink, multisig = Env().deploy_full_app()
        self.assertEqual(factory.storage["default_smak_token_type"](), {
                         "fa12": smak_token.address})
        self.assertEqual(factory.storage["default_sink"](), sink.address)
        self.assertEqual(sink.storage["factory_address"](), factory.address)
