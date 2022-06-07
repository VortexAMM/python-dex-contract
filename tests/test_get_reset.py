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
SHELL = "http://localhost:8732"

_using_params = dict(shell=SHELL, key=ALICE_KEY)
send_conf = dict(min_confirmations=1)
bob_using_params = dict(shell=SHELL, key=BOB_KEY)
charlie_using_params = dict(shell=SHELL, key=CHARLIE_KEY)

pytezos = pytezos.using(**_using_params)
bob_pytezos = pytezos.using(**bob_using_params)
charlie_pytezos = pytezos.using(**charlie_using_params)

with open("../michelson/get_reset.tz", encoding="UTF-8") as file:
    michelson = file.read()

get_reset = ContractInterface.from_michelson(michelson).using(**_using_params)

opg = get_reset.originate(initial_storage=0).send(**send_conf)

get_reset_addr = OperationResult.from_operation_group(
    opg.opg_result)[0].originated_contracts[0]

get_reset = pytezos.contract(get_reset_addr).using(**_using_params)

get_reset.getReset().send(**send_conf)
