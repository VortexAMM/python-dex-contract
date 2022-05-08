from time import sleep

from math import sqrt

from pendulum import period
from flat_curve import newton
from env import Env, ALICE_PK, pytezos, FA12Storage, FA2Storage, LqtStorage, send_conf, _using_params, BOB_PK, bob_pytezos, FactoryStorage
from test_factory import lp_metadata, lp_token_metadata
import unittest
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult

import logging
logging.basicConfig(level=logging.INFO)


accurancy_multiplier = 10 ** 12


class TestDex(unittest.TestCase):
    @staticmethod
    def print_title(instance):
        print("-----------------------------------")
        print("Test DEX: " + instance.__class__.__name__ + "...")
        print("-----------------------------------")

    @staticmethod
    def print_start(function_name):
        print("-----------------------------------")
        print("running test: " + function_name)
        print("-----------------------------------")

    @staticmethod
    def print_success(function_name):
        print("-----------------------------------")
        print(function_name + "... ok")
        print("-----------------------------------")

    class TestAddLiquidity(unittest.TestCase):
        def test0_before_tests(self):
            TestDex.print_title(self)

        def test1_it_adds_liquidity_successfuly(self):
            TestDex.print_start("test1_it_adds_liquidity_successfuly")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_address = dex.storage["lqt_address"]()
            lqt = pytezos.contract(lqt_address).using(**_using_params)
            alice_liquidity = lqt.storage["tokens"][ALICE_PK]()
            lqt_total = dex.storage["lqt_total"]()
            add_amount_a = 10 ** 6
            add_liquidity_params = {
                "owner": ALICE_PK,
                "amount_token_a": add_amount_a,
                "min_lqt_minted": add_amount_a * lqt_total // amount_a,
                "max_tokens_deposited": add_amount_a * amount_b // amount_a,
                "deadline": pytezos.now() + 100,
            }
            token_a.mint({"address": ALICE_PK, "value": add_amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": dex.address,
                            "value": add_amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                         ).send(**send_conf)
            token_b.approve({"spender": dex.address,
                            "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
            dex.addLiquidity(add_liquidity_params).send(**send_conf)
            self.assertEqual(dex.storage["lqt_total"](
            ), lqt_total + add_amount_a * lqt_total // amount_a)
            self.assertEqual(dex.storage["token_pool_a"](
            ), add_amount_a + amount_a)
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b + add_amount_a * amount_b // amount_a)
            self.assertEqual(lqt.storage["tokens"][ALICE_PK](
            ), alice_liquidity + add_amount_a * lqt_total // amount_a)

            TestDex.print_success(
                "test1_it_adds_liquidity_successfuly")

        def test2_it_adds_liquidity_with_xtz_successfully(self):
            TestDex.print_start(
                "test2_it_adds_liquidity_with_xtz_successfully")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_address = dex.storage["lqt_address"]()
            lqt = pytezos.contract(lqt_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            add_amount_a = 10 ** 6
            add_liquidity_params = {
                "owner": ALICE_PK,
                "amount_token_a": add_amount_a,
                "min_lqt_minted": add_amount_a * lqt_total // amount_a,
                "max_tokens_deposited": add_amount_a * amount_b // amount_a,
                "deadline": pytezos.now() + 100,
            }
            token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                         ).send(**send_conf)
            token_b.approve({"spender": dex.address,
                            "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
            dex.addLiquidity(add_liquidity_params).with_amount(
                add_amount_a).send(**send_conf)
            self.assertEqual(dex.context.get_balance(),
                             amount_a + add_amount_a)
            self.assertEqual(dex.storage["token_pool_a"]
                             (), amount_a + add_amount_a)
            new_liquidity = lqt_total + add_amount_a * lqt_total / amount_a
            self.assertEqual(dex.storage["lqt_total"](), new_liquidity)
            self.assertEqual(lqt.storage["tokens"][ALICE_PK](), new_liquidity)
            TestDex.print_success(
                "test2_it_adds_liquidity_with_xtz_successfully")

        def test3_it_fails_when_max_tokens_deposited_is_less_than_tokens_deposited(self):
            TestDex.print_start(
                "test3_it_fails_when_max_tokens_deposited_is_less_than_tokens_deposited")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            add_amount_a = 10 ** 6
            add_liquidity_params = {
                "owner": ALICE_PK,
                "amount_token_a": add_amount_a,
                "min_lqt_minted": add_amount_a * lqt_total // amount_a,
                "max_tokens_deposited": add_amount_a * amount_b // amount_a,
                "deadline": pytezos.now() + 100,
            }
            token_a.mint({"address": ALICE_PK, "value": add_amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": dex.address,
                            "value": add_amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                         ).send(**send_conf)
            token_b.approve({"spender": dex.address,
                            "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                add_liquidity_params["max_tokens_deposited"] = add_amount_a * \
                    amount_b // amount_a - 1
                dex.addLiquidity(add_liquidity_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "203"})
            TestDex.print_success(
                "test3_it_fails_when_max_tokens_deposited_is_less_than_tokens_deposited")

        def test4_it_fails_when_lqt_minted_is_less_than_min_lqt_minted(self):
            TestDex.print_start(
                "test4_it_fails_when_lqt_minted_is_less_than_min_lqt_minted")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            add_amount_a = 10 ** 6
            add_liquidity_params = {
                "owner": ALICE_PK,
                "amount_token_a": add_amount_a,
                "min_lqt_minted": add_amount_a * lqt_total // amount_a,
                "max_tokens_deposited": add_amount_a * amount_b // amount_a,
                "deadline": pytezos.now() + 100,
            }
            token_a.mint({"address": ALICE_PK, "value": add_amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": dex.address,
                            "value": add_amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                         ).send(**send_conf)
            token_b.approve({"spender": dex.address,
                            "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                add_liquidity_params["min_lqt_minted"] = add_amount_a * \
                    lqt_total // amount_a + 1
                dex.addLiquidity(add_liquidity_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "204"})
            TestDex.print_success(
                "test4_it_fails_when_lqt_minted_is_less_than_min_lqt_minted")

        def test5_it_fails_when_incorrect_xtz_amount_is_sent(self):
            TestDex.print_start(
                "test5_it_fails_when_incorrect_xtz_amount_is_sent")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_address = dex.storage["lqt_address"]()
            lqt = pytezos.contract(lqt_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            add_amount_a = 10 ** 6
            add_liquidity_params = {
                "owner": ALICE_PK,
                "amount_token_a": add_amount_a,
                "min_lqt_minted": add_amount_a * lqt_total // amount_a,
                "max_tokens_deposited": add_amount_a * amount_b // amount_a,
                "deadline": pytezos.now() + 100,
            }
            token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                         ).send(**send_conf)
            token_b.approve({"spender": dex.address,
                            "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                dex.addLiquidity(add_liquidity_params).with_amount(
                    add_amount_a + 1).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "217"})
            TestDex.print_success(
                "test5_it_fails_when_incorrect_xtz_amount_is_sent")

    class TestRemoveLiquidity(unittest.TestCase):
        def test0_before_tests(self):
            TestDex.print_title(self)

        def test1_it_removes_liquidity_successfuly(self):
            TestDex.print_start("test1_it_removes_liquidity_successfuly")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            remove_amount = 10 ** 6
            remove_liquidity_params = {
                "rem_to": ALICE_PK,
                "lqt_burned": remove_amount,
                "min_token_a_withdrawn": remove_amount * amount_a // lqt_total,
                "min_token_b_withdrawn": remove_amount * amount_b // lqt_total,
                "deadline": pytezos.now() + 100,
            }
            dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
            TestDex.print_success(
                "test1_it_removes_liquidity_successfuly")

        def test2_it_removes_liquidity_with_baker_rewards_update(self):
            TestDex.print_start(
                "test2_it_removes_liquidity_with_baker_rewards_update")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            remove_amount = 10 ** 6
            remove_liquidity_params = {
                "rem_to": ALICE_PK,
                "lqt_burned": remove_amount,
                "min_token_a_withdrawn": remove_amount * amount_a // lqt_total,
                "min_token_b_withdrawn": remove_amount * amount_b // lqt_total,
                "deadline": pytezos.now() + 100,
            }
            dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
            self.assertEqual(dex.storage["user_rewards"][ALICE_PK](), {
                             'reward': 0, 'reward_paid': 0})
            TestDex.print_success(
                "test2_it_removes_liquidity_with_baker_rewards_update")

        def test3_it_fails_when_token_a_withdrawn_is_less_than_min_tokens_withdrawn(self):
            TestDex.print_start(
                "test3_it_fails_when_token_a_withdrawn_is_less_than_min_tokens_withdrawn")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            remove_amount = lqt_total // 100
            remove_liquidity_params = {
                "rem_to": ALICE_PK,
                "lqt_burned": remove_amount,
                "min_token_a_withdrawn": remove_amount * amount_a // lqt_total,
                "min_token_b_withdrawn": remove_amount * amount_b // lqt_total,
                "deadline": pytezos.now() + 100,
            }
            with self.assertRaises(MichelsonError) as err:
                remove_liquidity_params["min_token_a_withdrawn"] = remove_amount * \
                    amount_a // lqt_total + 1
                dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "211"})
            TestDex.print_success(
                "test3_it_fails_when_token_a_withdrawn_is_lesser_than_min_tokens_withdrawn")

        def test4_it_fails_when_token_b_withdrawn_is_lesser_than_min_tokens_withdrawn(self):
            TestDex.print_start(
                "test4_it_fails_when_token_b_withdrawn_is_lesser_than_min_tokens_withdrawn")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            remove_amount = lqt_total // 100
            remove_liquidity_params = {
                "rem_to": ALICE_PK,
                "lqt_burned": remove_amount,
                "min_token_a_withdrawn": remove_amount * amount_a // lqt_total,
                "min_token_b_withdrawn": remove_amount * amount_b // lqt_total,
                "deadline": pytezos.now() + 100,
            }
            with self.assertRaises(MichelsonError) as err:
                remove_liquidity_params["min_token_b_withdrawn"] = remove_amount * \
                    amount_b // lqt_total + 1
                dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "219"})
            TestDex.print_success(
                "test4_it_fails_when_token_b_withdrawn_is_lesser_than_min_tokens_withdrawn")

        def test5_it_fails_when_burn_amount_is_greater_than_the_total_lqt(self):
            TestDex.print_start(
                "test5_it_fails_when_burn_amount_is_greater_than_the_total_lqt")
            factory, _, _, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            lqt_total = dex.storage["lqt_total"]()
            remove_amount = lqt_total + 1
            remove_liquidity_params = {
                "rem_to": ALICE_PK,
                "lqt_burned": remove_amount,
                "min_token_a_withdrawn": remove_amount * amount_a // lqt_total,
                "min_token_b_withdrawn": remove_amount * amount_b // lqt_total,
                "deadline": pytezos.now() + 100,
            }
            with self.assertRaises(MichelsonError) as err:
                dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "212"})
            TestDex.print_success(
                "test5_it_fails_when_burn_amount_is_greater_than_the_total_lqt")

    class TestSwap(unittest.TestCase):
        def test0_before_tests(self):
            TestDex.print_title(self)

        def test1_it_swaps_successfully_fa12_xtz(self):
            TestDex.print_start("test1_it_swaps_successfully_fa12_xtz")
            factory, _, sink, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"xtz": None},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"mutez": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_b).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"xtz": None})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "value": tokens_sold}
                         ).send(**send_conf)
            token_a.approve({"spender": dex_address,
                            "value": tokens_sold}).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            resp = dex.swap(swap_params).send(**send_conf)

            internal_operations = resp.opg_result["contents"][0]["metadata"][
                "internal_operation_results"
            ]
            self.assertEqual(
                internal_operations[3]["destination"], ALICE_PK
            )
            self.assertEqual(int(internal_operations[3]["amount"]), bought)

            self.assertEqual(
                sink.storage["burn"][{"fa12": token_a.address}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa12": token_a.address}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_a - bought)
            self.assertEqual(token_a.storage["tokens"][dex_address](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            TestDex.print_success(
                "test1_it_swaps_successfully_fa12_xtz")

        def test2_it_swaps_successfully_xtz_fa12(self):
            TestDex.print_start("test2_it_swaps_successfully_xtz_fa12")
            factory, _, sink, _ = Env().deploy_full_app()
            fa12_init_storage = FA12Storage()
            token_b = Env().deploy_fa12(fa12_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_a},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }

            token_b.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            resp = dex.swap(swap_params).with_amount(
                tokens_sold).send(**send_conf)

            internal_operations = resp.opg_result["contents"][0]["metadata"][
                "internal_operation_results"
            ]
            self.assertEqual(
                internal_operations[0]["destination"], sink.address
            )
            self.assertEqual(
                int(internal_operations[0]["amount"]), burn_amount + reserve_amount)

            self.assertEqual(
                sink.storage["burn"][{"xtz": None}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"xtz": None}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["tokens"][dex_address](
            ), amount_b - bought)
            TestDex.print_success(
                "test2_it_swaps_successfully_xtz_fa12")

        def test3_it_swaps_successfully_fa2_xtz(self):
            TestDex.print_start("test3_it_swaps_successfully_fa2_xtz")
            factory, _, sink, _ = Env().deploy_full_app()
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"xtz": None},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"mutez": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "amount": amount_a,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_b).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa2": (token_a.address, 0)}, {"xtz": None})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "amount": tokens_sold,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": dex_address, "token_id": 0}}]).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            resp = dex.swap(swap_params).send(**send_conf)

            internal_operations = resp.opg_result["contents"][0]["metadata"][
                "internal_operation_results"
            ]
            self.assertEqual(
                internal_operations[3]["destination"], ALICE_PK
            )
            self.assertEqual(int(internal_operations[3]["amount"]), bought)

            self.assertEqual(
                sink.storage["burn"][{"fa2": (token_a.address, 0)}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa2": (token_a.address, 0)}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_a - bought)
            self.assertEqual(token_a.storage["ledger"][(dex_address, 0)](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            TestDex.print_success(
                "test3_it_swaps_successfully_fa2_xtz")

        def test4_it_swaps_successfully_xtz_fa2(self):
            TestDex.print_start("test4_it_swaps_successfully_xtz_fa2")
            factory, _, sink, _ = Env().deploy_full_app()
            token_b = Env().deploy_fa2(FA2Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_b.mint({"address": ALICE_PK, "amount": amount_b,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_b.mint({"address": ALICE_PK, "amount": tokens_sold,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": dex_address, "token_id": 0}}]).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            resp = dex.swap(swap_params).with_amount(
                tokens_sold).send(**send_conf)

            internal_operations = resp.opg_result["contents"][0]["metadata"][
                "internal_operation_results"
            ]

            self.assertEqual(
                internal_operations[0]["destination"], sink.address
            )
            self.assertEqual(
                int(internal_operations[0]["amount"]), burn_amount + reserve_amount)

            self.assertEqual(
                sink.storage["burn"][{"xtz": None}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"xtz": None}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["ledger"][(dex_address, 0)](
            ), amount_b - bought)
            TestDex.print_success(
                "test4_it_swaps_successfully_xtz_fa2")

        def test5_it_swaps_successfully_fa12_fa2(self):
            TestDex.print_start("test5_it_swaps_successfully_fa12_fa2")
            factory, _, sink, _ = Env().deploy_full_app()
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa2(fa2_init_storage)
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "amount": amount_b,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "value": tokens_sold}
                         ).send(**send_conf)
            token_a.approve({"spender": dex_address,
                            "value": tokens_sold}).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            dex.swap(swap_params).send(**send_conf)

            self.assertEqual(
                sink.storage["burn"][{"fa12": token_a.address}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa12": token_a.address}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(token_a.storage["tokens"][dex_address](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["ledger"][(dex_address, 0)](
            ), amount_b - bought)
            TestDex.print_success(
                "test5_it_swaps_successfully_fa12_fa2")

        def test6_it_swaps_successfully_fa2_fa12(self):
            TestDex.print_start("test6_it_swaps_successfully_fa2_fa12")
            factory, _, sink, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa2(FA2Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "amount": amount_a,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa2": (token_a.address, 0)}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "amount": tokens_sold,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": dex_address, "token_id": 0}}]).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            dex.swap(swap_params).send(**send_conf)

            self.assertEqual(
                sink.storage["burn"][{"fa2": (token_a.address, 0)}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa2": (token_a.address, 0)}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(token_a.storage["ledger"][(dex_address, 0)](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["tokens"][dex_address](
            ), amount_b - bought)
            TestDex.print_success(
                "test6_it_swaps_successfully_fa2_fa12")

        def test7_it_swaps_successfully_fa12_fa12(self):
            TestDex.print_start("test7_it_swaps_successfully_fa12_fa12")
            factory, _, sink, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "value": tokens_sold}
                         ).send(**send_conf)
            token_a.approve({"spender": dex_address,
                            "value": tokens_sold}).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            dex.swap(swap_params).send(**send_conf)

            self.assertEqual(
                sink.storage["burn"][{"fa12": token_a.address}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa12": token_a.address}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(token_a.storage["tokens"][dex_address](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["tokens"][dex_address](
            ), amount_b - bought)
            TestDex.print_success(
                "test7_it_swaps_successfully_fa12_fa12")

        def test8_it_swaps_successfully_fa2_fa2(self):
            TestDex.print_start("test8_it_swaps_successfully_fa2_fa2")
            factory, _, sink, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa2(FA2Storage())
            token_b = Env().deploy_fa2(FA2Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "amount": amount_a,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "amount": amount_b,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa2": (token_a.address, 0)}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "amount": tokens_sold,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": dex_address, "token_id": 0}}]).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            dex.swap(swap_params).send(**send_conf)

            self.assertEqual(
                sink.storage["burn"][{"fa2": (token_a.address, 0)}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa2": (token_a.address, 0)}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(token_a.storage["ledger"][(dex_address, 0)](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["ledger"][(dex_address, 0)](
            ), amount_b - bought)
            TestDex.print_success(
                "test8_it_swaps_successfully_fa2_fa2")

        def test9_it_swaps_successfully_fa12_fa12_flat(self):
            TestDex.print_start("test9_it_swaps_successfully_fa12_fa12_flat")
            factory, _, sink, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"flat": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "value": tokens_sold}
                         ).send(**send_conf)
            token_a.approve({"spender": dex_address,
                            "value": tokens_sold}).send(**send_conf)
            burn_amount = tokens_sold * 2 // 10 ** 4
            reserve_amount = tokens_sold // 10 ** 4
            tokens_in = tokens_sold * 9990 // 10 ** 4
            f = (abs((amount_a + amount_b) ** 8) - ((amount_a - amount_b) ** 8))
            # for pegged tokens with pool sizes 10 ** 6 and tokens_in = 10 ** 4 * 9990 // 10 ** 4 = 9990, bought is 9989
            bought = newton(amount_a, amount_b, tokens_in, 0, f, 5)
            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            dex.swap(swap_params).send(**send_conf)

            self.assertEqual(
                sink.storage["burn"][{"fa12": token_a.address}](), burn_amount)
            self.assertEqual(
                sink.storage["reserve"][{"fa12": token_a.address}](), reserve_amount)

            self.assertEqual(dex.storage["token_pool_a"](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(token_a.storage["tokens"][dex_address](
            ), amount_a + tokens_sold - (burn_amount + reserve_amount))
            self.assertEqual(dex.storage["token_pool_b"](
            ), amount_b - bought)
            self.assertEqual(token_b.storage["tokens"][dex_address](
            ), amount_b - bought)
            launch_exchange_params["curve"] = {"product": None}
            TestDex.print_success(
                "test9_it_swaps_successfully_fa12_fa12_flat")

        def skip_test10_it_compares_curve_swaps_fa12_fa12_flat(self):
            TestDex.print_start(
                "skip_test10_it_compares_curve_swaps_fa12_fa12_flat")
            factory, _, _, _ = Env().deploy_full_app()
            liquidity_token = Env().deploy_liquidity_token(LqtStorage())
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"xtz": None},
                "token_amount_a": {"amount": 0},
                "token_amount_b": {"amount": 0},
                "curve": {"flat": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            launch_exchange_params["lp_address"] = liquidity_token.address
            for n in range(20):
                token_a = Env().deploy_fa12(FA12Storage())
                token_b = Env().deploy_fa12(FA12Storage())
                token_c = Env().deploy_fa12(FA12Storage())
                amount_a = 10 ** 12
                pool_multiplier = (n + 1) / 10 if n < 10 else (n - 8)
                amount_b = amount_a * (n + 1) // \
                    10 if n < 10 else amount_a * (n - 8)
                token_a.mint({"address": ALICE_PK, "value": 2 * amount_a}
                             ).send(**send_conf)
                token_a.approve({"spender": factory.address,
                                "value": 2 * amount_a}).send(**send_conf)
                token_b.mint({"address": ALICE_PK, "value": amount_b}
                             ).send(**send_conf)
                token_b.approve({"spender": factory.address,
                                "value": amount_b}).send(**send_conf)
                token_c.mint({"address": ALICE_PK, "value": amount_b}
                             ).send(**send_conf)
                token_c.approve({"spender": factory.address,
                                "value": amount_b}).send(**send_conf)

                launch_exchange_params["token_type_a"] = {
                    "fa12": token_a.address}
                launch_exchange_params["token_type_b"] = {
                    "fa12": token_b.address}
                launch_exchange_params["token_amount_a"] = {"amount": amount_a}
                launch_exchange_params["token_amount_b"] = {"amount": amount_b}
                launch_exchange_params["curve"] = {"product": None}
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)

                launch_exchange_params["token_type_a"] = {
                    "fa12": token_a.address}
                launch_exchange_params["token_type_b"] = {
                    "fa12": token_c.address}
                launch_exchange_params["token_amount_a"] = {"amount": amount_a}
                launch_exchange_params["token_amount_b"] = {"amount": amount_b}
                launch_exchange_params["curve"] = {"flat": None}
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)

                dex_1_address = factory.storage["pairs"][(
                    {"fa12": token_a.address}, {"fa12": token_b.address})]()
                dex_1 = pytezos.contract(dex_1_address).using(**_using_params)

                dex_2_address = factory.storage["pairs"][(
                    {"fa12": token_a.address}, {"fa12": token_c.address})]()
                dex_2 = pytezos.contract(dex_2_address).using(**_using_params)

                tokens_sold = 10 ** 10
                token_a.mint({"address": ALICE_PK, "value": 2 * tokens_sold}
                             ).send(**send_conf)
                token_a.approve({"spender": dex_1_address,
                                "value": tokens_sold}).send(**send_conf)
                f = (abs((amount_a + amount_b) ** 8) -
                     ((amount_a - amount_b) ** 8))
                swap_params = {
                    "t2t_to": BOB_PK,
                    "tokens_sold": tokens_sold,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10 ** 3
                }

                dex_1.swap(swap_params).send(**send_conf)
                amount_bought_product = token_b.storage["tokens"][BOB_PK]()
                ratio_product = tokens_sold / amount_bought_product

                swap_params = {
                    "t2t_to": BOB_PK,
                    "tokens_sold": tokens_sold,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10 ** 3
                }

                token_a.approve({"spender": dex_2_address,
                                "value": tokens_sold}).send(**send_conf)

                dex_2.swap(swap_params).send(**send_conf)
                amount_bought_flat = token_c.storage["tokens"][BOB_PK]()

                pool_ratio = 1 / pool_multiplier

                ratio_flat = tokens_sold / amount_bought_flat

                with open('../../compare_curve.txt', 'a') as f:
                    f.write(
                        f'token_pool_a : {amount_a} tokens; token_pool_b : {amount_b} tokens; \n')
                    f.write(
                        f'pool ratio : {pool_ratio} \n')
                    f.write(
                        f'constant-product : {tokens_sold} tokens sold; {amount_bought_product} tokens bought; \n')
                    f.write(
                        f'constant product exchange ratio : {ratio_product} \n')
                    f.write(
                        f'flat-curve : {tokens_sold} tokens sold; {amount_bought_flat} tokens bought; \n')
                    f.write(
                        f'flat curve exchange ratio : {ratio_flat} \n\n')
                launch_exchange_params["curve"] = {"product": None}
            TestDex.print_success(
                "skip_test10_it_compares_curve_swaps_fa12_fa12_flat")

        def test11_it_fails_when_token_is_xtz_and_no_amount_was_sent(self):
            TestDex.print_start(
                "test11_it_fails_when_token_is_xtz_and_no_amount_was_sent")
            factory, _, _, _ = Env().deploy_full_app()
            token_b = Env().deploy_fa2(FA2Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_b.mint({"address": ALICE_PK, "amount": amount_b,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_b.mint({"address": ALICE_PK, "amount": tokens_sold,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": dex_address, "token_id": 0}}]).send(**send_conf)
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            with self.assertRaises(MichelsonError) as err:
                dex.swap(swap_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "238"})
            TestDex.print_success(
                "test11_it_fails_when_token_is_xtz_and_no_amount_was_sent")

        def test12_it_fails_when_token_is_not_xtz_and_amount_is_sent(self):
            TestDex.print_start(
                "test12_it_fails_when_token_is_not_xtz_and_amount_is_sent")
            factory, _, _, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "value": tokens_sold}
                         ).send(**send_conf)
            token_a.approve({"spender": dex_address,
                            "value": tokens_sold}).send(**send_conf)
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            with self.assertRaises(MichelsonError) as err:
                dex.swap(swap_params).with_amount(
                    tokens_sold).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "231"})
            TestDex.print_success(
                "test12_it_fails_when_token_is_not_xtz_and_amount_is_sent")

        def test13_it_fails_when_tokens_bought_below_min_tokens_bought(self):
            TestDex.print_start(
                "test13_it_fails_when_tokens_bought_below_min_tokens_bought")
            factory, _, _, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "value": amount_a}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address,
                            "value": amount_a}).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "value": amount_b}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address,
                            "value": amount_b}).send(**send_conf)
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa12": token_a.address}, {"fa12": token_b.address})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            tokens_sold = 10 ** 4
            token_a.mint({"address": ALICE_PK, "value": tokens_sold}
                         ).send(**send_conf)
            token_a.approve({"spender": dex_address,
                            "value": tokens_sold}).send(**send_conf)
            tokens_in = tokens_sold * 9972 // 10 ** 4
            bought = (tokens_in * amount_b) // (amount_a + tokens_in)

            swap_params = {
                "t2t_to": ALICE_PK,
                "tokens_sold": tokens_sold,
                "min_tokens_bought": bought + 1,
                "a_to_b": True,
                "deadline": pytezos.now() + 10 ** 3
            }

            with self.assertRaises(MichelsonError) as err:
                dex.swap(swap_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "215"})
            TestDex.print_success(
                "test13_it_fails_when_tokens_bought_below_min_tokens_bought")

    class TestClaimReward(unittest.TestCase):
        def test0_before_tests(self):
            TestDex.print_title(self)

        def test1_it_claims_rewards_successfully_one_deposit(self):
            TestDex.print_start(
                "test1_it_claims_rewards_successfully_one_deposit")
            factory, _, _, _ = Env().deploy_full_app()
            token_b = Env().deploy_fa2(FA2Storage())

            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_b.mint({"address": ALICE_PK, "amount": amount_b,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            liquidity_token = dex.storage["lqt_address"]()
            liquidity_token = pytezos.using(
                **_using_params).contract(liquidity_token)

            sleep(15)

            added_amount = 10 ** 4

            pytezos.transaction(destination=dex.address,
                                amount=added_amount).send(**send_conf)

            dex_balance = dex.context.get_balance()

            self.assertEqual(dex_balance, amount_a + added_amount)

            self.assertEqual(dex.storage["total_reward"](), added_amount)

            self.assertLessEqual(dex.storage["reward_per_share"](
            ), added_amount * accurancy_multiplier // amount_a)

            self.assertGreaterEqual(dex.storage["reward_per_share"](
            ), added_amount * accurancy_multiplier // amount_a - 1)

            sleep(15)

            resp = dex.claimReward(ALICE_PK).send(**send_conf)

            alice_shares = int(sqrt(amount_a * amount_b))

            alice_reward_paid = alice_shares * \
                dex.storage["reward_per_share"]()

            self.assertEqual(
                alice_reward_paid, dex.storage["user_rewards"][ALICE_PK]["reward_paid"]())

            internal_operations = resp.opg_result["contents"][0]["metadata"]["internal_operation_results"]
            self.assertEqual(
                internal_operations[0]["destination"], ALICE_PK
            )
            self.assertGreaterEqual(
                int(internal_operations[0]["amount"]), added_amount - 1)

            self.assertLessEqual(
                int(internal_operations[0]["amount"]), added_amount)

            dex_balance = dex.context.get_balance()

            self.assertLessEqual(dex_balance, amount_a + 1)

            self.assertGreaterEqual(dex_balance, amount_a)
            TestDex.print_success(
                "test1_it_claims_rewards_successfully_one_deposit")

        def test2_it_claims_reward_successfully_multiple_deposits(self):
            TestDex.print_start(
                "test2_it_claims_reward_successfully_multiple_deposits")
            factory, _, _, _ = Env().deploy_full_app()
            token_b = Env().deploy_fa2(FA2Storage())

            amount_a = 10 ** 6
            amount_b = 10 ** 6
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_b.mint({"address": ALICE_PK, "amount": amount_b,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            liquidity_token = dex.storage["lqt_address"]()
            liquidity_token = pytezos.using(
                **_using_params).contract(liquidity_token)

            sleep(15)

            added_amount = 10 ** 4

            n = 6

            for i in range(n):
                pytezos.transaction(destination=dex.address,
                                    amount=added_amount).send(**send_conf)

            dex_balance = dex.context.get_balance()

            self.assertEqual(dex_balance, amount_a + added_amount * n)

            self.assertEqual(dex.storage["total_reward"](), added_amount * n)

            self.assertLessEqual(dex.storage["reward_per_share"](
            ), added_amount * n * accurancy_multiplier // amount_a)

            self.assertGreaterEqual(dex.storage["reward_per_share"](
            ), added_amount * n * accurancy_multiplier // amount_a - 1)

            sleep(15)

            resp = dex.claimReward(ALICE_PK).send(**send_conf)

            self.assertEqual(dex_balance, amount_a + n * added_amount)

            alice_shares = int(sqrt(amount_a * amount_b))

            alice_reward_paid = alice_shares * \
                dex.storage["reward_per_share"]()

            self.assertEqual(
                alice_reward_paid, dex.storage["user_rewards"][ALICE_PK]["reward_paid"]())

            internal_operations = resp.opg_result["contents"][0]["metadata"]["internal_operation_results"]
            self.assertEqual(
                internal_operations[0]["destination"], ALICE_PK
            )
            self.assertGreaterEqual(
                int(internal_operations[0]["amount"]), added_amount * n - 1)

            self.assertLessEqual(
                int(internal_operations[0]["amount"]), added_amount * n)

            dex_balance = dex.context.get_balance()

            self.assertLessEqual(dex_balance, amount_a + 1)

            self.assertGreaterEqual(dex_balance, amount_a)
            TestDex.print_success(
                "test2_it_claims_reward_successfully_multiple_deposits")

        def test3_it_claims_reward_successfully_two_lps(self):
            TestDex.print_start("test3_it_claims_reward_successfully_two_lps")
            factory, _, _, _ = Env().deploy_full_app()
            token_b = Env().deploy_fa2(FA2Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6

            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_b.mint({"address": ALICE_PK, "amount": amount_b * 2,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)

            liquidity_token = dex.storage["lqt_address"]()
            liquidity_token = pytezos.using(
                **_using_params).contract(liquidity_token)

            token_pool_a = dex.storage["token_pool_a"]()

            self.assertEqual(token_pool_a, amount_a)

            alice_shares = liquidity_token.storage["tokens"][ALICE_PK]()

            self.assertEqual(alice_shares, sqrt(amount_a * amount_b))

            total_lqt = dex.storage["lqt_total"]()

            self.assertEqual(total_lqt, alice_shares)

            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": dex_address, "token_id": 0}}]).send(**send_conf)

            add_liquidity_params = {
                "owner": BOB_PK,
                "amount_token_a": amount_a,
                "min_lqt_minted": 0,
                "max_tokens_deposited": amount_b,
                "deadline": pytezos.now() + 1000,
            }

            dex.addLiquidity(add_liquidity_params).with_amount(
                amount_a).send(**send_conf)

            bob_shares = liquidity_token.storage["tokens"][BOB_PK]()

            self.assertEqual(bob_shares, amount_a * total_lqt // token_pool_a)

            total_lqt = alice_shares + bob_shares

            self.assertEqual(total_lqt, sqrt(
                amount_a * amount_b) + sqrt(amount_a * amount_b))

            self.assertEqual(total_lqt, dex.storage["lqt_total"]())

            sleep(15)

            added_amount = 10 ** 4

            pytezos.transaction(destination=dex.address,
                                amount=added_amount).send(**send_conf)

            dex_balance = dex.context.get_balance()

            self.assertEqual(dex_balance, amount_a * 2 + added_amount)

            sleep(15)

            resp = dex.claimReward(ALICE_PK).send(**send_conf)

            internal_operations = resp.opg_result["contents"][0]["metadata"]["internal_operation_results"]
            self.assertEqual(
                internal_operations[0]["destination"], ALICE_PK
            )
            self.assertGreaterEqual(
                int(internal_operations[0]["amount"]), added_amount // 2 - 1)

            self.assertLessEqual(
                int(internal_operations[0]["amount"]), added_amount // 2)

            reward_per_share = added_amount * accurancy_multiplier // total_lqt

            self.assertGreaterEqual(
                reward_per_share, dex.storage["reward_per_share"]())

            self.assertLessEqual(reward_per_share - 1,
                                 dex.storage["reward_per_share"]())

            alice_reward_paid = alice_shares * \
                dex.storage["reward_per_share"]()

            self.assertEqual(
                alice_reward_paid, dex.storage["user_rewards"][ALICE_PK]["reward_paid"]())

            dex_balance = dex.context.get_balance()

            self.assertLessEqual(dex_balance, amount_a *
                                 2 + added_amount // 2 + 1)

            self.assertGreaterEqual(
                dex_balance, amount_a * 2 + added_amount // 2)

            dex.claimReward(ALICE_PK).send(**send_conf)
            self.assertEqual(dex.storage["user_rewards"]
                             [ALICE_PK]["reward_paid"](), alice_reward_paid)

            self.assertEqual(dex.context.get_balance(), dex_balance)

            resp = bob_pytezos.contract(dex.address).claimReward(
                ALICE_PK).send(**send_conf)

            self.assertGreaterEqual(
                reward_per_share, dex.storage["reward_per_share"]())

            self.assertLessEqual(reward_per_share - 1,
                                 dex.storage["reward_per_share"]())

            bob_reward_paid = bob_shares * dex.storage["reward_per_share"]()

            self.assertEqual(
                bob_reward_paid, dex.storage["user_rewards"][BOB_PK]["reward_paid"]())

            self.assertLessEqual(dex.context.get_balance(),
                                 dex_balance - bob_reward_paid // accurancy_multiplier)
            TestDex.print_success(
                "test3_it_claims_reward_successfully_two_lps")

    class TestDefault(unittest.TestCase):
        def test0_before_tests(self):
            TestDex.print_title(self)

        def test1_it_deposits_xtz(self):
            TestDex.print_start("test1_it_deposits_xtz")
            factory, _, _, _ = Env().deploy_full_app()
            token_b = Env().deploy_fa2(FA2Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6

            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_b.mint({"address": ALICE_PK, "amount": amount_b * 2,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"xtz": None}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            deposit = 10 ** 4
            pytezos.transaction(destination=dex_address,
                                amount=deposit).send(**send_conf)
            period_finish = dex.storage["period_finish"]()
            last_update_time = dex.storage["last_update_time"]()
            reward_per_sec = dex.storage["reward_per_sec"]()
            reward_per_share = dex.storage["reward_per_share"]()
            lqt_total = dex.storage["lqt_total"]()
            rewards_time = period_finish if pytezos.now() > period_finish else pytezos.now()
            new_reward = (rewards_time - last_update_time) * reward_per_sec
            reward_per_share = reward_per_share + new_reward // lqt_total
            xtz_pool = dex.storage["token_pool_a"]()
            total_reward = abs(dex.context.get_balance() - xtz_pool)
            self.assertEqual(dex.storage["reward"](), new_reward)
            self.assertEqual(
                dex.storage["reward_per_share"](), reward_per_share)
            self.assertEqual(
                dex.storage["last_update_time"](), last_update_time)
            self.assertEqual(dex.storage["reward_per_sec"](), reward_per_sec)
            self.assertEqual(dex.storage["period_finish"](), period_finish)
            self.assertEqual(dex.storage["total_reward"](), total_reward)

            TestDex.print_success(
                "test1_it_deposits_xtz")

        def test2_it_fails_if_no_pool_is_xtz(self):
            TestDex.print_start("test1_it_deposits_xtz")
            factory, _, _, _ = Env().deploy_full_app()
            token_a = Env().deploy_fa2(FA2Storage())
            token_b = Env().deploy_fa2(FA2Storage())
            amount_a = 10 ** 6
            amount_b = 10 ** 6

            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": amount_a},
                "token_amount_b": {"amount": amount_b},
                "curve": {"product": None},
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            token_a.mint({"address": ALICE_PK, "amount": amount_a * 2,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_a.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            token_b.mint({"address": ALICE_PK, "amount": amount_b * 2,
                          "metadata": {}, "token_id": 0}).send(**send_conf)
            token_b.update_operators([{"add_operator": {
                "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(
                amount_a).send(**send_conf)
            dex_address = factory.storage["pairs"][(
                {"fa2": (token_a.address, 0)}, {"fa2": (token_b.address, 0)})]()
            dex = pytezos.contract(dex_address).using(**_using_params)
            deposit = 10 ** 4
            with self.assertRaises(MichelsonError) as err:
                pytezos.transaction(destination=dex_address,
                                    amount=deposit).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "231"})

    def test_inner_test_class(self):
        test_classes_to_run = [
            self.TestAddLiquidity,
            self.TestRemoveLiquidity,
            self.TestSwap,
            self.TestClaimReward,
            self.TestDefault,
        ]
        suites_list = []
        for test_class in test_classes_to_run:
            suites_list.append(
                unittest.TestLoader().loadTestsFromTestCase(test_class))

        big_suite = unittest.TestSuite(suites_list)
        unittest.TextTestRunner().run(big_suite)


if __name__ == "__main__":
    unittest.main()
