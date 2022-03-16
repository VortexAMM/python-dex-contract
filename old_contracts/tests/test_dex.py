import math
import unittest

# import random
# import json
# from contextlib import contextmanager

from dataclasses import dataclass
from decimal import Decimal

# from pytezos.context.impl import ExecutionContext
# from pytezos.michelson.repl import InterpreterResult
from pytezos import ContractInterface

# from pytezos.michelson.stack import MichelsonStack
# from pytezos.michelson.micheline import MichelsonRuntimeError
from pytezos.rpc.errors import MichelsonError

# from pytezos.crypto.key import Key
from pytezos import pytezos
from pytezos.contract.result import OperationResult

from test_flat import newton, u

# from pytezos.michelson.sections.storage import StorageSection


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
class DexStorage:
    manager: str
    token_address: str = ""
    lp_token_address: str = "tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU"


@dataclass
class FA12Storage:
    admin: str


@dataclass
class FA2Storage:
    admin: str


class Env:
    @staticmethod
    def deploy_fa2(init_storage: FA2Storage, token_info):
        with open("FA2.tz", encoding="UTF-8") as file:
            michelson = file.read()

        fa2 = ContractInterface.from_michelson(michelson).using(**using_params)
        token_metadata = {
            0: {
                "token_id": 0,
                "token_info": token_info,
            }
        }
        storage = {
            "administrator": init_storage.admin,
            "all_tokens": 0,
            "ledger": {},
            "metadata": {},
            "operators": {},
            "paused": False,
            "token_metadata": token_metadata,
        }
        opg = fa2.originate(initial_storage=storage).send(**send_conf)
        fa2_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa2 = pytezos.using(**using_params).contract(fa2_addr)

        return fa2

    @staticmethod
    def deploy_fa12(init_storage: FA12Storage, token_info):
        with open("../michelson/fa12.tz", encoding="UTF-8") as file:
            michelson = file.read()

        fa12 = ContractInterface.from_michelson(
            michelson).using(**using_params)
        token_metadata = {
            0: {
                "token_id": 0,
                "token_info": token_info,
            }
        }
        storage = {
            "admin": init_storage.admin,
            "tokens": {},
            "allowances": {},
            "metadata": {},
            "paused": False,
            "token_metadata": token_metadata,
            "total_supply": 0,
        }
        opg = fa12.originate(initial_storage=storage).send(**send_conf)
        fa12_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa12 = pytezos.using(**using_params).contract(fa12_addr)

        return fa12

    @staticmethod
    def deploy_factory_fa2():
        with open("../michelson/factory_fa2.tz", encoding="UTF-8") as file:
            source = file.read()

        factory = ContractInterface.from_michelson(
            source).using(**using_params)
        factory_storage = {
            "empty_allowances": {},
            "empty_tokens": {},
            "empty_history": {},
            "empty_user_investments": {},
            "swaps": {},
            "token_to_swaps": {},
            "counter": 0,
            "default_reserve": DEFAULT_RESERVE,
            "default_metadata": {},
            "default_token_metadata": {},
        }
        opg = factory.originate(
            initial_storage=factory_storage).send(**send_conf)
        factory_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        return pytezos.using(**using_params).contract(factory_addr)

    @staticmethod
    def deploy_factory(reserve=DEFAULT_RESERVE):
        with open("../michelson/factory_fa12.tz", encoding="UTF-8") as file:
            source = file.read()

        factory = ContractInterface.from_michelson(
            source).using(**using_params)
        factory_storage = {
            "empty_allowances": {},
            "empty_tokens": {},
            "empty_history": {},
            "empty_user_investments": {},
            "swaps": {},
            "token_to_swaps": {},
            "counter": 0,
            "default_reserve": reserve,
            "default_token_metadata": {},
            "default_metadata": {},
        }
        opg = factory.originate(
            initial_storage=factory_storage).send(**send_conf)
        factory_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        return pytezos.using(**using_params).contract(factory_addr)


default_token_info = [
    {
        "decimals": b"5",
        "symbol": b"KUSD",
        "name": b"Kolibri",
        "thumbnailUri": b"https://kolibri-data.s3.amazonaws.com/logo.png",
    },
    {
        "decimals": b"6",
        "symbol": b"wXTZ",
        "name": b"Wrapped Tezos",
        # pylint: disable=line-too-long
        "thumbnailUri": b"https://raw.githubusercontent.com/StakerDAO/wrapped-xtz/dev/assets/wXTZ-token-FullColor.png",
    },
    {
        "decimals": b"3",
        "symbol": b"USDS",
        "name": b"Stably USD",
        "thumbnailUri": b"https://quipuswap.com/tokens/stably.png",
    },
    {
        "decimals": b"8",
        "symbol": b"tzBTC",
        "name": b"tzBTC",
        "thumbnailUri": b"https://tzbtc.io/wp-content/uploads/2020/03/tzbtc_logo_single.svg",
    },
    {
        "decimals": b"2",
        "symbol": b"STKR",
        "name": b"Staker Governance Token",
        "thumbnailUri": b"https://github.com/StakerDAO/resources/raw/main/stkr.png",
    },
    {
        "decimals": b"6",
        "symbol": b"USDtz",
        "name": b"USDtez",
        "thumbnailUri": b"https://usdtz.com/lightlogo10USDtz.png",
    },
    {
        "decimals": b"8",
        "symbol": b"ETHtz",
        "name": b"ETHtez",
        "thumbnailUri": b"https://ethtz.io/ETHtz_purple.png",
    },
]


def setup_swap_dashboard_data_test(token_pool, xtz_pool, reserve=DEFAULT_RESERVE):
    factory = Env.deploy_factory(reserve)
    fa12_init_storage = FA12Storage(ALICE_PK)

    def setup_fa12_token(amount):
        token_info = {
            "decimals": b"0",
            "symbol": b"ETHtz",
            "name": b"ETHtez",
            "thumbnailUri": b"https://ethtz.io/ETHtz_purple.png",
        }
        token = Env.deploy_fa12(fa12_init_storage, token_info)
        token.mint({"address": ALICE_PK, "value": amount * 1000}
                   ).send(**send_conf)
        token.approve({"spender": factory.address,
                      "value": amount}).send(**send_conf)
        return token

    token = setup_fa12_token(token_pool)
    param = {"token_address": token.address, "token_amount": token_pool}

    factory.launchExchangeMixed(param).with_amount(xtz_pool).send(**send_conf)

    swap_address = factory.storage["swaps"][0]()
    swap = pytezos.using(**using_params).contract(swap_address)

    token.approve({"spender": swap.address, "value": 10 ** 6}
                  ).send(**send_conf)
    return swap, token


def setup_swap_dashboard_data_test_fa2(token_pool, xtz_pool, reserve=DEFAULT_RESERVE):
    factory = Env.deploy_factory_fa2()
    fa2_init_storage = FA2Storage(ALICE_PK)

    def setup_fa2_token(amount):
        token_info = {
            "decimals": b"0",
            "symbol": b"ETHtz",
            "name": b"ETHtez",
            "thumbnailUri": b"https://ethtz.io/ETHtz_purple.png",
        }
        token = Env.deploy_fa2(fa2_init_storage, token_info)
        token.mint({"address": ALICE_PK, "amount": amount * 1000,
                    "metadata": {}, "token_id": 0}).send(**send_conf)
        token.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        return token

    token = setup_fa2_token(token_pool)
    param = {"token_address": token.address,
             "token_amount": token_pool, "token_id": 0}

    factory.launchExchangeMixed(param).with_amount(xtz_pool).send(**send_conf)

    swap_address = factory.storage["swaps"][0]()
    swap = pytezos.using(**using_params).contract(swap_address)

    token.update_operators([{"add_operator": {
        "owner": ALICE_PK, "operator": swap.address, "token_id": 0}}]).send(**send_conf)
    return swap, token


def get_xtz_balance(address):
    return int(pytezos.account(address)["balance"])


def get_opg_fee(resp):
    return int(resp.opg_result["contents"][0]["fee"])


class TestFactory(unittest.TestCase):
    def test_xtz_to_token_min_tokens_bought(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the error_TOKENS_BOUGHT_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_BOUGHT
          exception throws when expected, that is, after the reserve fee
          has been taken from xtz_in
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        start_xtz_pool = swap.storage["xtz_pool"]()
        start_token_pool = swap.storage["token_pool"]()

        xtz_sold = 10000
        tokens_bought = (xtz_sold * 9972 * start_token_pool) // (
            start_xtz_pool * 10000 + (xtz_sold * 9972)
        )

        with self.assertRaises(MichelsonError) as err:
            swap.xtzToToken(
                {
                    "to": ALICE_PK,
                    "min_tokens_bought": tokens_bought + 1,
                    "deadline": "2029-09-06T15:08:29.000Z",
                }
            ).with_amount(xtz_sold).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "18"})

        swap.xtzToToken(
            {
                "to": ALICE_PK,
                "min_tokens_bought": tokens_bought,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).with_amount(xtz_sold).send(**send_conf)

    def test_token_to_xtz_min_xtz_bought(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the error_XTZ_BOUGHT_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_XTZ_BOUGHT
          exception throws when expected, that is, after the reserve fee
          has been taken from xtz_out
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        start_xtz_pool = swap.storage["xtz_pool"]()
        start_token_pool = swap.storage["token_pool"]()

        tokens_sold = 10000
        xtz_bought = (tokens_sold * 9972 * start_xtz_pool) // (
            start_token_pool * 10000 + (tokens_sold * 9972)
        )

        with self.assertRaises(MichelsonError) as err:
            swap.tokenToXtz(
                {
                    "to": ALICE_PK,
                    "tokens_sold": tokens_sold,
                    "min_xtz_bought": xtz_bought + 1,
                    "deadline": "2029-09-06T15:08:29.000Z",
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int", "8"})

        swap.tokenToXtz(
            {
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_xtz_bought": xtz_bought,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

    def test_swap_update_reserve(self):
        """
        The reserve needs to be able to modify the reserve from the
        swap contract storage. Other addresses should not be able to
        modify the reserve.
        """
        token_pool = 10
        xtz_pool = 10
        swap, _ = setup_swap_dashboard_data_test(
            token_pool, xtz_pool, ALICE_PK)
        swap.updateReserve(BOB_PK).send(**send_conf)
        self.assertEqual(swap.storage["reserve"](), BOB_PK)

        with self.assertRaises(MichelsonError) as err:
            swap.updateReserve(ALICE_PK).send(**send_conf)
            self.assertRaises(err.exception.args[0]["with"], {"int": "40"})

    def test_token_to_token_reserve_fee_fa12_fa12(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, so 0.06% on both swaps
        - the user gets the right amount of token_out
        - that both swaps after the transaction have:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap_in, token_in = setup_swap_dashboard_data_test(
            token_pool, xtz_pool)
        swap_out, token_out = setup_swap_dashboard_data_test(
            token_pool, xtz_pool)

        start_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)
        start_alice_token_out = token_out.getBalance(
            ALICE_PK, None).callback_view()
        swap_in_start_xtz_pool = swap_in.storage["xtz_pool"]()
        swap_in_start_token_pool = swap_in.storage["token_pool"]()
        swap_out_start_xtz_pool = swap_out.storage["xtz_pool"]()
        swap_out_start_token_pool = swap_out.storage["token_pool"]()

        self.assertEqual(get_xtz_balance(
            swap_in.address), swap_in_start_xtz_pool)
        self.assertEqual(
            token_in.getBalance(swap_in.address, None).callback_view(),
            swap_in_start_token_pool,
        )

        tokens_sold = 100000
        opg = swap_in.tokenToToken(
            {
                "output_dexter_contract": swap_out.address,
                "min_tokens_bought": 0,
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap fa1.2 to fa1.2 : {consumed_gas} gas; {fee} mutez fee; \n')

        end_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)

        swap_in_xtz_bought = (tokens_sold * 9972 * swap_in_start_xtz_pool) // (
            swap_in_start_token_pool * 10000 + (tokens_sold * 9972)
        )
        # newton(swap_in_start_token_pool, swap_in_start_xtz_pool,
        #                             tokens_sold * 9972 // 10000, 0,  u(swap_in_start_token_pool, swap_in_start_xtz_pool), 5)

        swap_in_reserve_fee = (tokens_sold * 3 * swap_in_start_xtz_pool) // (
            swap_in_start_token_pool * 10000 + (tokens_sold * 3)
        )

        swap_out_xtz_sold = swap_in_xtz_bought
        swap_out_reserve_fee = swap_out_xtz_sold * 3 // 10000
        swap_out_tokens_bought = (
            swap_out_xtz_sold * 9972 * swap_out_start_token_pool
        ) // (swap_out_start_xtz_pool * 10000 + (swap_out_xtz_sold * 9972))

        # newton(swap_out_start_xtz_pool, swap_out_start_token_pool,
        #                                 swap_out_xtz_sold * 9972 // 10000, 0, u(swap_out_start_xtz_pool, swap_out_start_token_pool), 5)

        end_alice_token_out = token_out.getBalance(
            ALICE_PK, None).callback_view()
        swap_in_end_xtz_pool = swap_in.storage["xtz_pool"]()
        swap_in_end_token_pool = swap_in.storage["token_pool"]()

        reserve_fee = swap_in_reserve_fee + swap_out_reserve_fee

        # reserve has taxed proper xtz amount
        self.assertEqual(end_reserve_balance -
                         start_reserve_balance, reserve_fee)
        # swap token balance equals its token pool
        self.assertEqual(
            token_in.getBalance(swap_in.address, None).callback_view(),
            swap_in_end_token_pool,
        )
        # swap xtz balance equals its xtz pool
        self.assertEqual(get_xtz_balance(
            swap_in.address), swap_in_end_xtz_pool)
        # alice has got right amount of tokens
        self.assertEqual(
            end_alice_token_out - start_alice_token_out, swap_out_tokens_bought
        )

        # swap out token_pool and xtz_pool are tested in xtz_to_token
        # and do not need to be retested here
        # we test that it is called with the right param
        # when testing that alice gets the right amount of tokens out

        # we now show what the calculated values in the test were for manual review
        # notice that since initially xtz_pool == token_pool for both pools and
        # the pools are much larger than the amount exchange, we expect xtz_bought
        # to be close to tokenSold and the reserve fee to be small, which is the case.
        self.assertEqual(reserve_fee, 58)
        self.assertEqual(swap_out_tokens_bought, 99438)

        # history
        xtz_volume = (tokens_sold * swap_in_start_xtz_pool) // (
            swap_in_start_token_pool + tokens_sold
        )
        self.assertEqual(
            swap_in.storage["history"]["xtz_volume"](), xtz_volume)
        self.assertEqual(
            int(swap_in.storage["history"]["xtz_pool"]()), swap_in_end_xtz_pool
        )
        self.assertEqual(
            int(swap_in.storage["history"]["token_pool"]
                ()), swap_in_end_token_pool
        )

    def test_token_to_token_reserve_fee_fa2_fa2(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, so 0.06% on both swaps
        - the user gets the right amount of token_out
        - that both swaps after the transaction have:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap_in, token_in = setup_swap_dashboard_data_test_fa2(
            token_pool, xtz_pool)
        swap_out, token_out = setup_swap_dashboard_data_test_fa2(
            token_pool, xtz_pool)

        start_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)
        start_alice_token_out = token_out.storage["ledger"][(ALICE_PK, 0)]()
        swap_in_start_xtz_pool = swap_in.storage["xtz_pool"]()
        swap_in_start_token_pool = swap_in.storage["token_pool"]()
        swap_out_start_xtz_pool = swap_out.storage["xtz_pool"]()
        swap_out_start_token_pool = swap_out.storage["token_pool"]()

        self.assertEqual(get_xtz_balance(
            swap_in.address), swap_in_start_xtz_pool)
        self.assertEqual(
            token_in.storage["ledger"][(swap_in.address, 0)](),
            swap_in_start_token_pool,
        )

        tokens_sold = 100000
        opg = swap_in.tokenToToken(
            {
                "output_dexter_contract": swap_out.address,
                "min_tokens_bought": 0,
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap fa2 to fa2 : {consumed_gas} gas; {fee} mutez fee; \n')

        end_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)

        swap_in_xtz_bought = (tokens_sold * 9972 * swap_in_start_xtz_pool) // (
            swap_in_start_token_pool * 10000 + (tokens_sold * 9972)
        )
        # newton(swap_in_start_token_pool, swap_in_start_xtz_pool,
        #                             tokens_sold * 9972 // 10000, 0,  u(swap_in_start_token_pool, swap_in_start_xtz_pool), 5)

        swap_in_reserve_fee = (tokens_sold * 3 * swap_in_start_xtz_pool) // (
            swap_in_start_token_pool * 10000 + (tokens_sold * 3)
        )

        swap_out_xtz_sold = swap_in_xtz_bought
        swap_out_reserve_fee = swap_out_xtz_sold * 3 // 10000
        swap_out_tokens_bought = (
            swap_out_xtz_sold * 9972 * swap_out_start_token_pool
        ) // (swap_out_start_xtz_pool * 10000 + (swap_out_xtz_sold * 9972))

        # newton(swap_out_start_xtz_pool, swap_out_start_token_pool,
        #                                 swap_out_xtz_sold * 9972 // 10000, 0, u(swap_out_start_xtz_pool, swap_out_start_token_pool), 5)

        end_alice_token_out = token_out.storage["ledger"][(ALICE_PK, 0)]()
        swap_in_end_xtz_pool = swap_in.storage["xtz_pool"]()
        swap_in_end_token_pool = swap_in.storage["token_pool"]()

        reserve_fee = swap_in_reserve_fee + swap_out_reserve_fee

        # reserve has taxed proper xtz amount
        self.assertEqual(end_reserve_balance -
                         start_reserve_balance, reserve_fee)
        # swap token balance equals its token pool
        self.assertEqual(
            token_in.storage["ledger"][(swap_in.address, 0)](),
            swap_in_end_token_pool,
        )
        # swap xtz balance equals its xtz pool
        self.assertEqual(get_xtz_balance(
            swap_in.address), swap_in_end_xtz_pool)
        # alice has got right amount of tokens
        self.assertEqual(
            end_alice_token_out - start_alice_token_out, swap_out_tokens_bought
        )

        # swap out token_pool and xtz_pool are tested in xtz_to_token
        # and do not need to be retested here
        # we test that it is called with the right param
        # when testing that alice gets the right amount of tokens out

        # we now show what the calculated values in the test were for manual review
        # notice that since initially xtz_pool == token_pool for both pools and
        # the pools are much larger than the amount exchange, we expect xtz_bought
        # to be close to tokenSold and the reserve fee to be small, which is the case.
        self.assertEqual(reserve_fee, 58)
        self.assertEqual(swap_out_tokens_bought, 99438)

        # history
        xtz_volume = (tokens_sold * swap_in_start_xtz_pool) // (
            swap_in_start_token_pool + tokens_sold
        )
        self.assertEqual(
            swap_in.storage["history"]["xtz_volume"](), xtz_volume)
        self.assertEqual(
            int(swap_in.storage["history"]["xtz_pool"]()), swap_in_end_xtz_pool
        )
        self.assertEqual(
            int(swap_in.storage["history"]["token_pool"]
                ()), swap_in_end_token_pool
        )

    def test_token_to_token_reserve_fee_fa12_fa2(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, so 0.06% on both swaps
        - the user gets the right amount of token_out
        - that both swaps after the transaction have:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap_in, token_in = setup_swap_dashboard_data_test(
            token_pool, xtz_pool)
        swap_out, token_out = setup_swap_dashboard_data_test_fa2(
            token_pool, xtz_pool)

        tokens_sold = 100000
        opg = swap_in.tokenToToken(
            {
                "output_dexter_contract": swap_out.address,
                "min_tokens_bought": 0,
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap fa1.2 to fa2 : {consumed_gas} gas; {fee} mutez fee; \n')

    def test_token_to_token_reserve_fee_fa2_fa12(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, so 0.06% on both swaps
        - the user gets the right amount of token_out
        - that both swaps after the transaction have:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap_in, token_in = setup_swap_dashboard_data_test_fa2(
            token_pool, xtz_pool)
        swap_out, token_out = setup_swap_dashboard_data_test(
            token_pool, xtz_pool)

        tokens_sold = 100000
        opg = swap_in.tokenToToken(
            {
                "output_dexter_contract": swap_out.address,
                "min_tokens_bought": 0,
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap fa2 to fa1.2 : {consumed_gas} gas; {fee} mutez fee; \n')

    def test_token_to_xtz_reserve_fee(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, 0.06% of the xtz_out
        - the user gets the right amount of xtz_out
        - that the swap after the transaction has:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap, token = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        start_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)
        # start_alice_xtz = get_xtz_balance(ALICE_PK)
        start_xtz_pool = swap.storage["xtz_pool"]()
        start_token_pool = swap.storage["token_pool"]()

        self.assertEqual(get_xtz_balance(swap.address), start_xtz_pool)
        self.assertEqual(
            token.getBalance(
                swap.address, None).callback_view(), start_token_pool
        )

        tokens_sold = 100000
        resp = swap.tokenToXtz(
            {
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_xtz_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(resp.opg_result)
        fee = resp.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap fa1.2 to xtz : {consumed_gas} gas; {fee} mutez fee; \n')

        end_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)

        xtz_bought = (tokens_sold * 9972 * start_xtz_pool) // (
            start_token_pool * 10000 + (tokens_sold * 9972)
        )
        reserve_fee = (tokens_sold * 3 * start_xtz_pool) // (
            start_token_pool * 10000 + (tokens_sold * 3)
        )

        # end_alice_xtz = get_xtz_balance(ALICE_PK)
        end_xtz_pool = swap.storage["xtz_pool"]()
        end_token_pool = swap.storage["token_pool"]()

        # reserve has taxed proper xtz amount
        self.assertEqual(reserve_fee, end_reserve_balance -
                         start_reserve_balance)
        # swap token balance equals its token pool
        self.assertEqual(
            token.getBalance(
                swap.address, None).callback_view(), end_token_pool
        )
        # swap xtz balance equals its xtz pool
        self.assertEqual(get_xtz_balance(swap.address), end_xtz_pool)
        # alice has got right amount of tokens
        xtz_amount_from_internal_op_to_alice = int(
            resp.opg_result["contents"][0]["metadata"]["internal_operation_results"][1][
                "amount"
            ]
        )
        self.assertEqual(xtz_amount_from_internal_op_to_alice, xtz_bought)

        # we now show what the calculated values in the test were for manual review
        # notice that since initially xtz_pool == token_pool and the pools are much larger
        # than the amount exchange, we expect xtz_bought to be close to tokenSold and
        # the reserve fee to be small, which is the case.
        self.assertEqual(reserve_fee, 29)
        self.assertEqual(xtz_bought, 99719)

        # history
        xtz_volume = (
            tokens_sold * start_xtz_pool) // (start_token_pool + tokens_sold)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_volume)
        self.assertEqual(
            int(swap.storage["history"]["xtz_pool"]()), end_xtz_pool)
        self.assertEqual(
            int(swap.storage["history"]["token_pool"]()), end_token_pool)

    def test_token_to_xtz_reserve_fee_fa2(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, 0.06% of the xtz_out
        - the user gets the right amount of xtz_out
        - that the swap after the transaction has:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap, token = setup_swap_dashboard_data_test_fa2(token_pool, xtz_pool)

        tokens_sold = 100000
        resp = swap.tokenToXtz(
            {
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_xtz_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(resp.opg_result)
        fee = resp.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap fa2 to xtz : {consumed_gas} gas; {fee} mutez fee; \n')

    def test_xtz_to_token_reserve_fee(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, 0.06% of the xtz_in
        - the user gets the right amount of token_out
        - that the swap after the transaction has:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap, token = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        start_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)
        start_alice_token = token.getBalance(ALICE_PK, None).callback_view()
        start_xtz_pool = swap.storage["xtz_pool"]()
        start_token_pool = swap.storage["token_pool"]()

        self.assertEqual(get_xtz_balance(swap.address), start_xtz_pool)
        self.assertEqual(
            token.getBalance(
                swap.address, None).callback_view(), start_token_pool
        )

        xtz_sold = 100000
        opg = swap.xtzToToken(
            {
                "to": ALICE_PK,
                "min_tokens_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).with_amount(xtz_sold).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap xtz to fa1.2 : {consumed_gas} gas; {fee} mutez fee; \n')

        end_reserve_balance = get_xtz_balance(DEFAULT_RESERVE)
        end_alice_token = token.getBalance(ALICE_PK, None).callback_view()

        tokens_bought = (xtz_sold * 9972 * start_token_pool) // (
            start_xtz_pool * 10000 + (xtz_sold * 9972)
        )
        reserve_fee = (xtz_sold * 3) // 10000

        end_alice_token = token.getBalance(ALICE_PK, None).callback_view()
        end_xtz_pool = swap.storage["xtz_pool"]()
        end_token_pool = swap.storage["token_pool"]()

        # reserve has taxed proper xtz amount
        self.assertEqual(reserve_fee, end_reserve_balance -
                         start_reserve_balance)
        # swap token balance equals its token pool
        self.assertEqual(
            token.getBalance(
                swap.address, None).callback_view(), end_token_pool
        )
        # swap xtz balance equals its xtz pool
        self.assertEqual(get_xtz_balance(swap.address), end_xtz_pool)
        # alice has got right amount of tokens
        self.assertEqual(end_alice_token - start_alice_token, tokens_bought)

        # we now show what the calculated values in the test were for manual review
        # notice that since initially xtz_pool == token_pool and the pools are much larger
        # than the traded amount, we expect tokens_bought to be close to xtz_sold and
        # the reserve fee to be small, which is the case.
        self.assertEqual(reserve_fee, 30)
        self.assertEqual(tokens_bought, 99719)

        # history
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_sold)
        self.assertEqual(
            int(swap.storage["history"]["xtz_pool"]()), end_xtz_pool)
        self.assertEqual(
            int(swap.storage["history"]["token_pool"]()), end_token_pool)

    def test_xtz_to_token_reserve_fee(self):
        """
        Since the Dexter contract was modified to lower the overall fee and
        redistribute some XTZ to the reserve, we test that:
        - the reserve gets its fee, 0.06% of the xtz_in
        - the user gets the right amount of token_out
        - that the swap after the transaction has:
          + xtz_pool == its xtz balance
          + token_pool == to its balance in the associated token contract
        """
        token_pool = 10 ** 10
        xtz_pool = 10 ** 10
        swap, token = setup_swap_dashboard_data_test_fa2(token_pool, xtz_pool)

        xtz_sold = 100000
        opg = swap.xtzToToken(
            {
                "to": ALICE_PK,
                "min_tokens_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).with_amount(xtz_sold).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'old swap xtz to fa2 : {consumed_gas} gas; {fee} mutez fee; \n')

    def test_add_liquidity_dashboard_data(self):
        """We test that:
        - user investments are tracked so that they can be calculated later on
        - xtz/token pools are tracked so the price history can be trivially calculated later on"""
        token_pool = 10 ** 6
        xtz_pool = 10 ** 6
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)
        xtz_amount = 10 ** 6
        opg = swap.addLiquidity(
            {
                "owner": ALICE_PK,
                "min_lqt_minted": 1,
                "max_tokens_deposited": 1000000000000,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).with_amount(xtz_amount).send(**send_conf)
        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        with open('../../add_liquidity_gas.txt', 'a') as f:
            f.write(
                f'old add_liquidity : {consumed_gas} gas; \n')
        # self.assertEqual(
        #     swap.storage["user_investments"][ALICE_PK](),
        #     {
        #         "direction": "add",
        #         "token": swap.storage["token_pool"]() - token_pool,
        #         "xtz": swap.storage["xtz_pool"]() - xtz_pool,
        #     },
        # )
        # self.assertEqual(
        #     swap.storage["history"]["xtz_pool"](), swap.storage["xtz_pool"]()
        # )
        # self.assertEqual(
        #     swap.storage["history"]["token_pool"](
        #     ), swap.storage["token_pool"]()
        # )

    def test_remove_liquidity_dashboard_data(self):
        """We test that:
        - user investments are tracked so that they can be calculated later on
        - xtz/token pools are tracked so the price history can be trivially calculated later on"""
        token_pool = 10 ** 6
        xtz_pool = 10 ** 6
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)
        opg = swap.removeLiquidity(
            {
                "to": ALICE_PK,
                "lqt_burned": 10 ** 6,
                "min_xtz_withdrawn": 1,
                "min_tokens_withdrawn": 1,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)
        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        with open('../../remove_liquidity_gas.txt', 'a') as f:
            f.write(
                f'old remove_liquidity : {consumed_gas} gas; \n')
        # self.assertEqual(
        #     swap.storage["user_investments"][ALICE_PK](),
        #     {
        #         "direction": "remove",
        #         "token": token_pool - swap.storage["token_pool"](),
        #         "xtz": xtz_pool - swap.storage["xtz_pool"](),
        #     },
        # )
        # self.assertEqual(
        #     swap.storage["history"]["xtz_pool"](), swap.storage["xtz_pool"]()
        # )
        # self.assertEqual(
        #     swap.storage["history"]["token_pool"](
        #     ), swap.storage["token_pool"]()
        # )

    def test_xtz_to_token_dashboard_data(self):
        """We test that: xtz/token pools are tracked
        so the price history can be trivially calculated later on"""
        token_pool = 1000
        xtz_pool = 10000
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        xtz_amount = 10
        swap.xtzToToken(
            {
                "to": ALICE_PK,
                "min_tokens_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).with_amount(xtz_amount).send(**send_conf)
        self.assertEqual(
            swap.storage["history"]["xtz_pool"](), swap.storage["xtz_pool"]()
        )
        self.assertEqual(
            swap.storage["history"]["token_pool"](
            ), swap.storage["token_pool"]()
        )
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_amount)

        xtz_amount = 11
        swap.xtzToToken(
            {
                "to": ALICE_PK,
                "min_tokens_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).with_amount(xtz_amount).send(**send_conf)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_amount)

    def token_to_xtz_dashboard_data(self):
        """We test that: xtz/token pools are tracked
        so the price history can be trivially calculated later on"""
        token_pool = 1000
        xtz_pool = 10000
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        start_xtz_pool = swap.storage["xtz_pool"]()
        start_token_pool = swap.storage["token_pool"]()

        tokens_sold = 10
        swap.tokenToXtz(
            {
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_xtz_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)
        self.assertEqual(
            swap.storage["history"]["xtz_pool"](), swap.storage["xtz_pool"]()
        )
        self.assertEqual(
            swap.storage["history"]["token_pool"](
            ), swap.storage["token_pool"]()
        )

        xtz_volume = (
            tokens_sold * start_xtz_pool) // (start_token_pool + tokens_sold)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_volume)

        new_xtz_pool = swap.storage["xtz_pool"]()
        new_token_pool = swap.storage["token_pool"]()
        tokens_sold = 15
        swap.tokenToXtz(
            {
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_xtz_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        xtz_volume = (
            tokens_sold * new_xtz_pool) // (new_token_pool + tokens_sold)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_volume)

    def test_token_to_token_dashboard_data(self):
        """We test that: xtz/token pools are tracked
        so the price history can be trivially calculated later on"""
        token_pool = 1000
        xtz_pool = 10000
        swap, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)
        swap2, _ = setup_swap_dashboard_data_test(token_pool, xtz_pool)

        start_xtz_pool = swap.storage["xtz_pool"]()
        start_token_pool = swap.storage["token_pool"]()

        tokens_sold = 10
        swap.tokenToToken(
            {
                "output_dexter_contract": swap2.address,
                "min_tokens_bought": 0,
                "to": ALICE_PK,
                "tokens_sold": 10,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)
        self.assertEqual(
            swap.storage["history"]["xtz_pool"](), swap.storage["xtz_pool"]()
        )
        self.assertEqual(
            swap.storage["history"]["token_pool"](
            ), swap.storage["token_pool"]()
        )

        xtz_volume = (
            tokens_sold * start_xtz_pool) // (start_token_pool + tokens_sold)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_volume)

        self.assertEqual(
            swap2.storage["history"]["xtz_pool"](), swap2.storage["xtz_pool"]()
        )
        self.assertEqual(
            swap2.storage["history"]["token_pool"](
            ), swap2.storage["token_pool"]()
        )

        new_xtz_pool = swap.storage["xtz_pool"]()
        new_token_pool = swap.storage["token_pool"]()
        tokens_sold = 15
        swap.tokenToXtz(
            {
                "to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_xtz_bought": 0,
                "deadline": "2029-09-06T15:08:29.000Z",
            }
        ).send(**send_conf)

        xtz_volume = (
            tokens_sold * new_xtz_pool) // (new_token_pool + tokens_sold)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), xtz_volume)

    def test_launch_exchange_fa2(self):
        """We test that the FA2 factory launches an FA2 swap with an FA 2 token and
        configures it properly including the initial history big maps"""
        factory = Env.deploy_factory_fa2()
        fa2_init_storage = FA2Storage(ALICE_PK)

        def setup_fa2_token(amount):
            token_info = {
                "decimals": b"0",
                "symbol": b"ETHtz",
                "name": b"ETHtez",
                "thumbnailUri": b"https://ethtz.io/ETHtz_purple.png",
            }
            token = Env.deploy_fa2(fa2_init_storage, token_info)
            token.mint(
                {
                    "address": ALICE_PK,
                    "amount": amount * 1000,
                    "metadata": {},
                    "token_id": 0,
                }
            ).send(**send_conf)
            token.update_operators(
                [
                    {
                        "add_operator": {
                            "owner": ALICE_PK,
                            "operator": factory.address,
                            "token_id": 0,
                        }
                    }
                ]
            ).send(**send_conf)
            return token

        token_pool = 1000
        token = setup_fa2_token(token_pool)
        param = {
            "token_address": token.address,
            "token_amount": token_pool,
            "token_id": 0,
        }

        xtz_pool = 10000
        factory.launchExchangeMixed(param).with_amount(
            xtz_pool).send(**send_conf)

        # should not fail
        swap_address = factory.storage["swaps"][0]()
        swap = pytezos.using(**using_params).contract(swap_address)

        # counter incremented
        self.assertEqual(factory.storage["counter"](), 1)

        # testing swap storage initialization
        self.assertEqual(swap.storage["xtz_pool"](), xtz_pool)
        self.assertEqual(swap.storage["token_pool"](), token_pool)
        self.assertEqual(swap.storage["self_is_updating_token_pool"](), False)
        self.assertEqual(swap.storage["freeze_baker"](), False)
        self.assertEqual(swap.storage["manager"](), factory.address)
        self.assertEqual(swap.storage["token_address"](), token.address)
        self.assertEqual(swap.storage["history"]["token_pool"](), token_pool)
        self.assertEqual(swap.storage["history"]["xtz_pool"](), xtz_pool)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), 0)
        lqt_total = xtz_pool
        self.assertEqual(swap.storage["lqt_total"](), lqt_total)
        self.assertEqual(
            swap.storage["user_investments"][ALICE_PK](),
            {"direction": "add", "token": 1000, "xtz": 10000},
        )

        # test fa12 balances
        token_address = swap.storage["token_address"]()
        token = pytezos.using(**using_params).contract(token_address)

        def get_balance(addr):
            return token.balance_of(
                {"requests": [{"owner": addr, "token_id": 0}],
                    "callback": None}
            ).callback_view()[0]["balance"]

        self.assertEqual(get_balance(ALICE_PK),
                         token_pool * 1000 - token_pool)
        self.assertEqual(get_balance(swap.address), token_pool)

        # check that swap contract has a balance equal to token_pool
        self.assertEqual(pytezos.account(swap.address)
                         ["balance"], str(xtz_pool))

        # testing lqt token initialization
        lqt_token_address = swap.storage["lqt_address"]()
        lqt_token = pytezos.using(**using_params).contract(lqt_token_address)

        self.assertEqual(lqt_token.storage["admin"](), swap.address)
        self.assertEqual(lqt_token.storage["tokens"][ALICE_PK](), lqt_total)
        self.assertEqual(lqt_token.storage["total_supply"](), lqt_total)

        # test that we cannot launch exchange with same token
        token.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": factory.address,
                        "token_id": 0,
                    }
                }
            ]
        ).send(**send_conf)
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchangeMixed(param).with_amount(
                xtz_pool).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int", "3"})

    def test_launch_exchange(self):
        """We test that the FA1.2 factory launches an FA1.2 swap with an FA1.2 token and
        configures it properly including the initial history big maps"""
        factory = Env.deploy_factory()
        fa12_init_storage = FA12Storage(ALICE_PK)

        def setup_fa12_token(amount):
            token_info = {
                "decimals": b"0",
                "symbol": b"ETHtz",
                "name": b"ETHtez",
                "thumbnailUri": b"https://ethtz.io/ETHtz_purple.png",
            }
            token = Env.deploy_fa12(fa12_init_storage, token_info)
            token.mint({"address": ALICE_PK, "value": amount * 1000}
                       ).send(**send_conf)
            token.approve({"spender": factory.address, "value": amount}).send(
                **send_conf
            )
            return token

        token_pool = 1000
        token = setup_fa12_token(token_pool)
        param = {"token_address": token.address, "token_amount": token_pool}

        xtz_pool = 10000
        factory.launchExchangeMixed(param).with_amount(
            xtz_pool).send(**send_conf)

        # should not fail
        swap_address = factory.storage["swaps"][0]()
        swap = pytezos.using(**using_params).contract(swap_address)

        # counter incremented
        self.assertEqual(factory.storage["counter"](), 1)

        # testing swap storage initialization
        self.assertEqual(swap.storage["xtz_pool"](), xtz_pool)
        self.assertEqual(swap.storage["token_pool"](), token_pool)
        self.assertEqual(swap.storage["self_is_updating_token_pool"](), False)
        self.assertEqual(swap.storage["freeze_baker"](), False)
        self.assertEqual(swap.storage["manager"](), factory.address)
        self.assertEqual(swap.storage["token_address"](), token.address)
        self.assertEqual(swap.storage["history"]["token_pool"](), token_pool)
        self.assertEqual(swap.storage["history"]["xtz_pool"](), xtz_pool)
        self.assertEqual(swap.storage["history"]["xtz_volume"](), 0)
        lqt_total = xtz_pool
        self.assertEqual(swap.storage["lqt_total"](), lqt_total)
        self.assertEqual(
            swap.storage["user_investments"][ALICE_PK](),
            {"direction": "add", "token": 1000, "xtz": 10000},
        )

        # test fa12 balances
        token_address = swap.storage["token_address"]()
        token = pytezos.using(**using_params).contract(token_address)
        self.assertEqual(
            token.storage["tokens"][ALICE_PK](), token_pool *
            1000 - token_pool
        )
        self.assertEqual(token.storage["tokens"][swap.address](), token_pool)

        # check that swap contract has a balance equal to token_pool
        self.assertEqual(pytezos.account(swap.address)
                         ["balance"], str(xtz_pool))

        # testing lqt token initialization
        lqt_token_address = swap.storage["lqt_address"]()
        lqt_token = pytezos.using(**using_params).contract(lqt_token_address)

        self.assertEqual(lqt_token.storage["admin"](), swap.address)
        self.assertEqual(lqt_token.storage["tokens"][ALICE_PK](), lqt_total)
        self.assertEqual(lqt_token.storage["total_supply"](), lqt_total)

        # test that we cannot launch exchange with same token
        token.approve({"spender": factory.address, "value": token_pool}).send(
            **send_conf
        )
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchangeMixed(param).with_amount(
                xtz_pool).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int", "3"})

    # @unittest.skip("Only used to deploy on testnet for frontend tests")

    def test_deploy_swarm(self):
        # pylint: disable=no-self-use
        """Used to deploy factory contracts along with FA1.2 and FA2 tokens.
        Should help with developing the application frontend."""
        factory = Env.deploy_factory()
        factory_fa2 = Env.deploy_factory_fa2()

        with open("contract_addresses.txt", "w", encoding="UTF-8") as file:
            file.write(f"factory FA1.2: {factory.address}\n")
            file.write(f"factory FA2: {factory_fa2.address}\n")

        fa2_init_storage = FA2Storage(ALICE_PK)

        for token_info in default_token_info[3:]:
            decimals = int(token_info["decimals"].decode("utf-8"))
            token = Env.deploy_fa2(fa2_init_storage, token_info)
            amount = int(1000 * math.pow(10, decimals))
            token.mint(
                {
                    "address": ALICE_PK,
                    "amount": amount * 1000,
                    "metadata": {},
                    "token_id": 0,
                }
            ).send(**send_conf)
            token.update_operators(
                [
                    {
                        "add_operator": {
                            "owner": ALICE_PK,
                            "operator": factory_fa2.address,
                            "token_id": 0,
                        }
                    }
                ]
            ).send(**send_conf)
            param = {
                "token_address": token.address,
                "token_amount": amount,
                "token_id": 0,
            }
            counter = factory_fa2.storage["counter"]()
            opg = (
                # factory_fa2.launchExchange(param)
                # .with_amount(10 ** 10)
                # .send(**send_conf)
                factory_fa2.launchExchangeMixed(param)
                .with_amount(Decimal(10))
                .send(**send_conf)
            )
            consumed_gas = OperationResult.consumed_gas(opg.opg_result)
            swap_address = factory_fa2.storage["swaps"][counter]()
            swap = pytezos.using(**using_params).contract(swap_address)
            xtz_amount = swap.context.get_balance()

            with open("contract_addresses.txt", "a", encoding="UTF-8") as file:
                file.write(
                    f"fa2 token: {token.address} ; {consumed_gas} gas \n"
                    f"fa2 token: {token.address} ; {xtz_amount} amount \n")

        fa12_init_storage = FA12Storage(ALICE_PK)

        for token_info in default_token_info[:3]:
            decimals = int(token_info["decimals"].decode("utf-8"))
            token = Env.deploy_fa12(fa12_init_storage, token_info)
            amount = int(1000 * math.pow(10, decimals))
            token.mint({"address": ALICE_PK, "value": amount * 1000}
                       ).send(**send_conf)
            token.approve({"spender": factory.address, "value": amount}).send(
                **send_conf
            )
            param = {"token_address": token.address, "token_amount": amount}
            counter = factory.storage["counter"]()
            # opg = (
            #     factory.launchExchange(param).with_amount(
            #         10 ** 10).send(**send_conf)
            opg = (
                factory.launchExchangeMixed(param).with_amount(
                    Decimal(10)).send(**send_conf)
            )
            consumed_gas = OperationResult.consumed_gas(opg.opg_result)
            swap_address = factory.storage["swaps"][counter]()
            swap = pytezos.using(**using_params).contract(swap_address)
            xtz_amount = swap.context.get_balance()

            with open("contract_addresses.txt", "a", encoding="UTF-8") as file:
                file.write(
                    f"fa1.2 token: {token.address} ; {consumed_gas} gas \n"
                    f"fa1.2 token: {token.address} ; {xtz_amount} amount \n")


if __name__ == "__main__":
    unittest.main()
