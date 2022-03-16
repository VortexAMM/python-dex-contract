from dataclasses import dataclass, field
import struct
from click import option
from pytezos import pytezos, ContractInterface
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult

DEFAULT_RESERVE = "tz1VYKnRgPyfZjdsnoVPyQrhBuhWHoP5QqxM"


# sandbox
ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"
SHELL = "http://localhost:20000"


using_params = dict(shell=SHELL, key=ALICE_KEY)

pytezos = pytezos.using(**using_params)
send_conf = dict(min_confirmations=1)


@dataclass
class FactoryStorage:
    default_reserve: str = ""
    pairs: dict = field(default_factory=dict)
    pools: dict = field(default_factory=dict)
    default_smak_token_type: dict = field(default_factory=dict)
    default_lp_metadata: dict = field(default_factory=dict)
    default_lp_allowances: dict = field(default_factory=dict)
    default_lp_token_metadata: dict = field(default_factory=dict)
    counter: int = 0


class Factory(storage=FactoryStorage()):
    factory_storage = {
        "empty_allowances": {},
        "empty_tokens": {},
        "empty_history": {},
        "empty_user_investments": {},
        "swaps": {},
        "token_to_swaps": {},
        "counter": 0,
        "default_reserve": DEFAULT_RESERVE,
        "default_token_metadata": {},
        "default_metadata": {},
    }
    launch_exchange_params = {
        "token_address": str,
        "token_amount": int,
        "curve": {},
        "token_id": option(int)
    }

    def deploy_factory(self):
        with open("../michelson/factory_fa12.tz", encoding="UTF-8") as file:
            source = file.read()

        factory = ContractInterface.from_michelson(
            source).using(**using_params)
        storage = self.factory_storage
        opg = factory.originate(
            initial_storage=factory_storage).send(**send_conf)
        factory_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        factory = pytezos.using(**using_params).contract(factory_addr)
        return factory
