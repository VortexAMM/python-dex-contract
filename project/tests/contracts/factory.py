from pytezos import pytezos, ContractInterface
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult


class Factory:
    def deploy(init_storage):
        with open("../../michelson/factory.tz", encoding="UTF-8") as file:
            michelson = file.read()
        factory = ContractInterface.from_michelson(
            michelson).using(**using_params)
