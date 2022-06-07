import math
import unittest
import logging
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult
from data import default_token_info
from env import (
    Env,
    ALICE_PK,
    pytezos,
    FA12Storage,
    FA2Storage,
    FactoryStorage,
    send_conf,
    BOB_PK,
    bob_pytezos,
    MultisigStorage,
    SinkStorage,
)

logging.basicConfig(level=logging.INFO)

lp_metadata = {
    "name": "",
    "version": "",
    "homepage": "",
    "authors": [""],
}
lp_token_metadata = {
    "uri": "",
    "symbol": "",
    "decimals": "",
    "shouldPreferSymbol": "",
    "thumbnailUri": "",
}


class TestFactory(unittest.TestCase):
    @staticmethod
    def print_title(instance):
        print("Test Factory: " + instance.__class__.__name__ + "...")
        print("-----------------------------------")

    @staticmethod
    def print_start(function_name):
        print("-----------------------------------")
        print("running test: " + function_name)
        print("-----------------------------------")

    @staticmethod
    def print_success(function_name):
        print(function_name + "... ok")
        print("-----------------------------------")

    class LaunchExchange(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_launches_exchange(self):
            TestFactory.print_start("test1_it_launches_exchange")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            tokens = []
            fa12_init_storage = FA12Storage()
            for token_info in default_token_info[:3]:
                decimals = int(token_info["decimals"].decode("utf-8"))
                token_metadata = {
                    0: {
                        "token_id": 0,
                        "token_info": token_info,
                    }
                }
                fa12_init_storage.token_metadata = token_metadata
                token = Env().deploy_fa12(fa12_init_storage)
                token = {
                    "token_type": {"fa12": token.address},
                    "address": token.address,
                    "decimals": decimals,
                }
                tokens.append(token)
            fa2_init_storage = FA2Storage()
            for token_info in default_token_info[3:]:
                decimals = int(token_info["decimals"].decode("utf-8"))
                token_metadata = {
                    0: {
                        "token_id": 0,
                        "token_info": token_info,
                    }
                }
                fa2_init_storage.token_metadata = token_metadata
                token = Env().deploy_fa2(fa2_init_storage)
                token = {
                    "token_type": {"fa2": (token.address, 0)},
                    "address": token.address,
                    "decimals": decimals,
                }
                tokens.append(token)
            for i, token_a in enumerate(tokens[:]):
                decimals_a = token_a["decimals"]
                address_a = token_a["address"]
                amount_a = int(1000 * math.pow(10, decimals_a))
                amount_type_a = {"amount": amount_a}
                if token_a["token_type"] == {"fa12": address_a}:
                    pytezos.contract(address_a).mint(
                        {"address": ALICE_PK, "value": amount_a}
                    ).send(**send_conf)
                    pytezos.contract(address_a).approve(
                        {"spender": factory.address, "value": amount_a}
                    ).send(**send_conf)
                else:
                    pytezos.contract(address_a).mint(
                        {
                            "address": ALICE_PK,
                            "amount": amount_a,
                            "metadata": {},
                            "token_id": 0,
                        }
                    ).send(**send_conf)
                    pytezos.contract(address_a).update_operators(
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
                amount_b = amount_a
                amount_type_b = {"mutez": amount_b}
                launch_exchange_params = {
                    "token_type_a": token_a["token_type"],
                    "token_type_b": {"xtz": None},
                    "token_amount_a": amount_type_a,
                    "token_amount_b": amount_type_b,
                    "curve": "product",
                    "metadata": lp_metadata,
                    "token_metadata": lp_token_metadata,
                }

                factory.launchExchange(launch_exchange_params).with_amount(
                    amount_b).send(**send_conf)
                for token_b in tokens[i + 1:]:
                    decimals_b = token_a["decimals"]
                    address_b = token_b["address"]
                    amount_b = int(1000 * math.pow(10, decimals_b))
                    amount_type_b = {"amount": amount_b}
                    if token_a["token_type"] == {"fa12": address_a}:
                        pytezos.contract(address_a).mint(
                            {"address": ALICE_PK, "value": amount_a}
                        ).send(**send_conf)
                        pytezos.contract(address_a).approve(
                            {"spender": factory.address, "value": amount_a}
                        ).send(**send_conf)
                    else:
                        pytezos.contract(address_a).mint(
                            {
                                "address": ALICE_PK,
                                "amount": amount_a,
                                "metadata": {},
                                "token_id": 0,
                            }
                        ).send(**send_conf)
                        pytezos.contract(address_a).update_operators(
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
                    if token_b["token_type"] == {"fa12": address_b}:
                        pytezos.contract(address_b).mint(
                            {"address": ALICE_PK, "value": amount_b}
                        ).send(**send_conf)
                        pytezos.contract(address_b).approve(
                            {"spender": factory.address, "value": amount_b}
                        ).send(**send_conf)
                    else:
                        pytezos.contract(address_b).mint(
                            {
                                "address": ALICE_PK,
                                "amount": amount_b,
                                "metadata": {},
                                "token_id": 0,
                            }
                        ).send(**send_conf)
                        pytezos.contract(
                            token_b["token_type"]["fa2"][0]
                        ).update_operators(
                            [
                                {
                                    "add_operator": {
                                        "owner": ALICE_PK,
                                        "operator": factory.address,
                                        "token_id": 0,
                                    }
                                }
                            ]
                        ).send(
                            **send_conf
                        )
                    launch_exchange_params = {
                        "token_type_a": token_a["token_type"],
                        "token_type_b": token_b["token_type"],
                        "token_amount_a": amount_type_a,
                        "token_amount_b": amount_type_b,
                        "curve": "product",
                        "metadata": lp_metadata,
                        "token_metadata": lp_token_metadata,
                    }
                    factory.launchExchange(launch_exchange_params).send(
                        **send_conf
                    )

            TestFactory.print_success("test01_it_launches_exchange")

        def test02_it_fails_when_sink_is_not_deployed(self):
            TestFactory.print_start("test2_it_fails_when_sink_is_not_deployed")
            init_storage = FactoryStorage()
            factory = Env().deploy_factory(init_storage)
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "104"})
            TestFactory.print_success(
                "test02_it_fails_when_sink_is_not_deployed")

        def test03_it_fails_when_tokens_are_equal_fa12(self):
            TestFactory.print_start(
                "test3_it_fails_when_tokens_are_equal_fa12")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_a.address},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "101"})
            TestFactory.print_success(
                "test03_it_fails_when_tokens_are_equal_fa12")

        def test04_it_fails_when_tokens_are_equal_fa2(self):
            TestFactory.print_start("test4_it_fails_when_tokens_are_equal_fa2")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_a.address, 0)},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "101"})
            TestFactory.print_success(
                "test04_it_fails_when_tokens_are_equal_fa2")

        def test05_it_fails_when_tokens_are_equal_xtz(self):
            TestFactory.print_start("test5_it_fails_when_tokens_are_equal_xtz")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"xtz": None},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"mutez": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "101"})
            TestFactory.print_success(
                "test05_it_fails_when_tokens_are_equal_xtz")

        def test06_it_fails_when_pair_already_exists(self):
            TestFactory.print_start("test6_it_fails_when_pair_already_exists")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            fa12_init_storage = FA12Storage()
            token_b = Env().deploy_fa12(fa12_init_storage)
            token_b.mint({"address": ALICE_PK, "value": 10**6}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**6}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint({"address": ALICE_PK, "value": 10**6}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**6}).send(
                **send_conf
            )
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "102"})
            # also in reverse order
            launch_exchange_params = {
                "token_type_a": {"fa12": token_b.address},
                "token_type_b": {"fa2": (token_a.address, 0)},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "102"})
            TestFactory.print_success(
                "test06_it_fails_when_pair_already_exists")

        def test07_it_fails_when_pools_are_empty_fa12(self):
            TestFactory.print_start("test7_it_fails_when_pools_are_empty_fa12")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa12_init_storage = FA12Storage()
            token_a = Env().deploy_fa12(fa12_init_storage)
            token_b = Env().deploy_fa12(fa12_init_storage)
            token_a.mint({"address": ALICE_PK, "value": 10**6}
                         ).send(**send_conf)
            token_a.approve({"spender": factory.address, "value": 10**6}).send(
                **send_conf
            )
            token_b.mint({"address": ALICE_PK, "value": 10**6}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**6}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 0},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "103"})
            TestFactory.print_success(
                "test07_it_fails_when_pools_are_empty_fa12")

        def test08_it_fails_when_pools_are_empty_fa2(self):
            TestFactory.print_start("test8_it_fails_when_pools_are_empty_fa2")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            token_b = Env().deploy_fa2(fa2_init_storage)
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 0},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "103"})
            TestFactory.print_success(
                "test08_it_fails_when_pools_are_empty_fa2")

        def test09_it_fails_when_one_pool_is_xtz_and_amount_sent_not_equal_to_token_amount(
            self,
        ):
            TestFactory.print_start(
                "test09_it_fails_when_one_pool_is_xtz_and_amount_sent_not_equal_to_token_amount"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_b = Env().deploy_fa2(fa2_init_storage)
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6 + 1
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "132"})
            TestFactory.print_success(
                "test09_it_fails_when_one_pool_is_xtz_and_amount_sent_not_equal_to_token_amount"
            )

        def test10_it_fails_when_token_a_is_not_xtz_and_amount_is_mutez(self):
            TestFactory.print_start(
                "test10_it_fails_when_token_a_is_xtz_and_amount_is_amount"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            token_b = Env().deploy_fa2(fa2_init_storage)

            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "141"})
            TestFactory.print_success(
                "test10_it_fails_when_token_a_is_xtz_and_amount_is_amount"
            )

        def test11_it_fails_when_token_a_is_xtz_and_amount_is_amount(self):
            TestFactory.print_start(
                "test11_it_fails_when_token_a_is_xtz_and_amount_is_amount"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_b = Env().deploy_fa2(fa2_init_storage)
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "142"})
            TestFactory.print_success(
                "test11_it_fails_when_token_a_is_xtz_and_amount_is_amount"
            )

        def test12_it_fails_when_token_b_is_not_xtz_and_amount_is_mutez(self):
            TestFactory.print_start(
                "test12_it_fails_when_token_b_is_not_xtz_and_amount_is_mutez"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            token_b = Env().deploy_fa2(fa2_init_storage)

            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"mutez": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "143"})
            TestFactory.print_success(
                "test12_it_fails_when_token_b_is_not_xtz_and_amount_is_mutez"
            )

        def test13_it_fails_when_token_b_is_xtz_and_amount_is_amount(self):
            TestFactory.print_start(
                "test13_it_fails_when_token_b_is_xtz_and_amount_is_amount"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            launch_exchange_params = {
                "token_type_b": {"xtz": None},
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_amount_a": {"amount": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "144"})
            TestFactory.print_success(
                "test13_it_fails_when_token_b_is_xtz_and_amount_is_amount"
            )

        def test14_it_fails_when_curve_is_flat_and_pools_are_not_equal(self):
            TestFactory.print_start(
                "test14_it_fails_when_curve_is_flat_and_pools_are_not_equal"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_a = Env().deploy_fa2(fa2_init_storage)
            token_b = Env().deploy_fa2(fa2_init_storage)

            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"fa2": (token_a.address, 0)},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"amount": 10**5},
                "token_amount_b": {"amount": 10**6},
                "curve": "flat",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.launchExchange(launch_exchange_params).with_amount(
                    10**6
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "128"})
            TestFactory.print_success(
                "test14_it_fails_when_curve_is_flat_and_pools_are_not_equal"
            )

    class RemoveExchange(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_removes_an_exchange(self):
            TestFactory.print_start("test1_it_removes_an_exchange")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_b = Env().deploy_fa2(fa2_init_storage)
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )

            factory.removeExchange(
                {
                    "token_a": {"xtz": None},
                    "token_b": {"fa2": (token_b.address, 0)},
                    "index": 0,
                }
            ).send(**send_conf)

            with self.assertRaises(KeyError):
                factory.storage["pools"][0]()
            with self.assertRaises(KeyError):
                factory.storage["pairs"][
                    ({"xtz": None}, {"fa2": (token_b.address, 0)})
                ]()

        def test02_it_removes_an_exchange_threshold_two(self):
            TestFactory.print_start(
                "test2_it_removes_an_exchange_threshold_two")
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            fa2_init_storage = FA2Storage()
            token_b = Env().deploy_fa2(fa2_init_storage)
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_addr = factory.storage["pools"][0]()
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)

            remove_exchange_param = {
                "token_a": {"xtz": None},
                "token_b": {"fa2": (token_b.address, 0)},
                "index": 0,
            }

            factory.removeExchange(remove_exchange_param).send(**send_conf)

            self.assertEqual(factory.storage["pools"][0](), dex_addr)
            self.assertEqual(
                factory.storage["pairs"][
                    ({"xtz": None}, {"fa2": (token_b.address, 0)})
                ](),
                dex_addr,
            )

            bob_pytezos.contract(factory.address).removeExchange(
                remove_exchange_param
            ).send(**send_conf)

            with self.assertRaises(KeyError):
                factory.storage["pools"][0]()
            with self.assertRaises(KeyError):
                factory.storage["pairs"][
                    ({"xtz": None}, {"fa2": (token_b.address, 0)})
                ]()

        def test03_it_fails_when_no_pair_matches_tokens(self):
            TestFactory.print_start(
                "test3_it_fails_when_no_pair_matches_tokens")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            token_a = Env().deploy_fa2(FA2Storage())
            token_b = Env().deploy_fa2(FA2Storage())
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )

            remove_exchange_param = {
                "token_a": {"fa2": (token_a.address, 0)},
                "token_b": {"fa2": (token_b.address, 0)},
                "index": 0,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.removeExchange(remove_exchange_param).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "136"})

        def test04_it_fails_when_index_not_listed_in_pools(self):
            TestFactory.print_start(
                "test4_it_fails_when_index_not_listed_in_pools")
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            token_a = Env().deploy_fa2(FA2Storage())
            token_b = Env().deploy_fa2(FA2Storage())
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )

            remove_exchange_param = {
                "token_a": {"xtz": None},
                "token_b": {"fa2": (token_b.address, 0)},
                "index": 1,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.removeExchange(remove_exchange_param).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "137"})

        def test05_it_fails_when_pair_and_index_are_of_different_exchanges(self):
            TestFactory.print_start(
                "test5_it_fails_when_pair_and_index_are_of_different_exchanges"
            )
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            token_a = Env().deploy_fa2(FA2Storage())
            token_b = Env().deploy_fa2(FA2Storage())
            token_a.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_a.update_operators(
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
            token_b.mint(
                {
                    "address": ALICE_PK,
                    "amount": 2 * 10**6,
                    "metadata": {},
                    "token_id": 0,
                }
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )

            launch_exchange_params["token_type_a"] = {
                "fa2": (token_a.address, 0)}
            launch_exchange_params["token_amount_a"] = {"amount": 10**6}
            factory.launchExchange(launch_exchange_params).send(**send_conf)

            remove_exchange_param = {
                "token_a": {"xtz": None},
                "token_b": {"fa2": (token_b.address, 0)},
                "index": 1,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.removeExchange(remove_exchange_param).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "138"})

    class LaunchSink(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_launches_sink(self):
            factory = Env().deploy_factory(FactoryStorage())
            self.assertIsNone(factory.storage["default_sink"]())
            factory.launchSink().send(**send_conf)
            self.assertIsNotNone(factory.storage["default_sink"]())

        def test02_it_launches_sink_with_threshold_2(self):
            factory = Env().deploy_factory(FactoryStorage())
            multisig_address = factory.storage["multisig"]()
            multisig = pytezos.using(
                **Env().using_params).contract(multisig_address)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            self.assertIsNone(factory.storage["default_sink"]())
            factory.launchSink().send(**send_conf)
            self.assertIsNone(factory.storage["default_sink"]())
            bob_pytezos.contract(
                factory.address).launchSink().send(**send_conf)
            self.assertIsNotNone(factory.storage["default_sink"]())

        def test03_it_fails_when_sink_has_been_deployed(self):
            factory = Env().deploy_factory(FactoryStorage())
            self.assertIsNone(factory.storage["default_sink"]())
            factory.launchSink().send(**send_conf)
            self.assertIsNotNone(factory.storage["default_sink"]())
            with self.assertRaises(MichelsonError) as err:
                factory.launchSink().send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "112"})

        def test04_it_fails_when_factory_is_not_authorized_by_multisig(self):
            factory = Env().deploy_factory(FactoryStorage())
            self.assertIsNone(factory.storage["default_sink"]())
            multisig_address = factory.storage["multisig"]()
            multisig = pytezos.using(
                **Env().using_params).contract(multisig_address)
            multisig.removeAuthorizedContract(
                factory.address).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                factory.launchSink().send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1009"})

        def test05_it_fails_when_alice_votes_twice(self):
            factory = Env().deploy_factory(FactoryStorage())
            multisig_address = factory.storage["multisig"]()
            multisig = pytezos.using(
                **Env().using_params).contract(multisig_address)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            self.assertIsNone(factory.storage["default_sink"]())
            factory.launchSink().send(**send_conf)
            self.assertIsNone(factory.storage["default_sink"]())
            with self.assertRaises(MichelsonError) as err:
                factory.launchSink().send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

        def test06_it_fails_when_bob_is_not_admin(self):
            factory = Env().deploy_factory(FactoryStorage())
            multisig_address = factory.storage["multisig"]()
            multisig = pytezos.using(
                **Env().using_params).contract(multisig_address)
            self.assertNotIn(BOB_PK, multisig.storage["admins"]())
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(
                    factory.address).launchSink().send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

    class SetLqtAddress(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_fails_when_called_directly(self):
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            with self.assertRaises(MichelsonError) as err:
                factory.setLqtAddress(
                    {"dex_address": ALICE_PK, "lqt_address": ALICE_PK}
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "109"})

    class SetSinkClaimLimit(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_sets_sink_claim_limit(self):
            factory, _, sink, _ = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            self.assertEqual(sink.storage["token_claim_limit"](), 100)

            factory.setSinkClaimLimit(20).send(**send_conf)
            self.assertEqual(sink.storage["token_claim_limit"](), 20)

        def test02_it_sets_sink_claim_limit_with_threshold_two(self):
            factory, _, sink, multisig = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            self.assertEqual(sink.storage["token_claim_limit"](), 100)
            factory.setSinkClaimLimit(20).send(**send_conf)
            self.assertEqual(sink.storage["token_claim_limit"](), 100)
            bob_pytezos.contract(factory.address).setSinkClaimLimit(20).send(
                **send_conf
            )
            self.assertEqual(sink.storage["token_claim_limit"](), 20)

        def test03_it_fails_when_bob_is_not_admin(self):
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(factory.address).setSinkClaimLimit(20).send(
                    **send_conf
                )
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test04_it_fails_when_factory_is_not_authorized_by_multisig(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            multisig.removeAuthorizedContract(
                factory.address).send(**send_conf)
            self.assertNotIn(
                factory.address, multisig.storage["authorized_contracts"]()
            )
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            with self.assertRaises(MichelsonError) as err:
                factory.setSinkClaimLimit(20).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1009"})

        def test05_it_fails_when_alice_calls_twice(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            factory.setSinkClaimLimit(20).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                factory.setSinkClaimLimit(20).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

    class UpdateBaker(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_updates_baker_for_one_pool(self):
            factory, _, _, _ = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            self.assertEqual(factory.storage["default_baker"](), ALICE_PK)
            # TODO: how do I get the delegate for dex?

    class UpdateMultisig(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_updates_multisig_successfully(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            multisig_storage = MultisigStorage(
                authorized_contracts=factory.address)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            new_multisig = Env().deploy_multisig(multisig_storage)
            factory.updateMultisig(new_multisig.address).send(**send_conf)
            self.assertEqual(
                factory.storage["multisig"](), new_multisig.address)
            self.assertIn(
                factory.address, new_multisig.storage["authorized_contracts"]()
            )
            self.assertIn(ALICE_PK, new_multisig.storage["admins"]())

        def test02_it_updates_multisig_with_threshold_2(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            multisig_storage = MultisigStorage(
                authorized_contracts=factory.address)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            new_multisig = Env().deploy_multisig(multisig_storage)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            factory.updateMultisig(new_multisig.address).send(**send_conf)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            bob_pytezos.contract(factory.address).updateMultisig(
                new_multisig.address
            ).send(**send_conf)
            self.assertEqual(
                factory.storage["multisig"](), new_multisig.address)
            self.assertIn(
                factory.address, new_multisig.storage["authorized_contracts"]()
            )
            self.assertIn(ALICE_PK, new_multisig.storage["admins"]())

        def test03_it_fails_when_caller_is_not_admin(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            multisig_storage = MultisigStorage(
                authorized_contracts=factory.address)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            new_multisig = Env().deploy_multisig(multisig_storage)
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(factory.address).updateMultisig(
                    new_multisig.address
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test04_it_fails_when_factory_is_not_authorized_by_multisig(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            multisig.removeAuthorizedContract(
                factory.address).send(**send_conf)
            multisig_storage = MultisigStorage(
                authorized_contracts=factory.address)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            new_multisig = Env().deploy_multisig(multisig_storage)
            with self.assertRaises(MichelsonError) as err:
                factory.updateMultisig(new_multisig.address).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1009"})

        def test05_it_fails_when_alice_votes_twice(self):
            factory, _, _, multisig = Env().deploy_full_app(ALICE_PK)
            multisig_storage = MultisigStorage(
                authorized_contracts=factory.address)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            new_multisig = Env().deploy_multisig(multisig_storage)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            factory.updateMultisig(new_multisig.address).send(**send_conf)
            self.assertEqual(factory.storage["multisig"](), multisig.address)
            with self.assertRaises(MichelsonError) as err:
                factory.updateMultisig(new_multisig.address).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

    class UpdateSinkAddress(unittest.TestCase):
        def test0_before_tests(self):
            TestFactory.print_title(self)

        def test01_it_updates_sink_address_one_exchange(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_address = factory.storage["pairs"][
                ({"xtz": None}, {"fa2": (token_b.address, 0)})
            ]()
            dex = pytezos.contract(dex_address).using(**Env().using_params)
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            self.assertEqual(dex.storage["sink"](), sink.address)
            new_sink_storage = SinkStorage
            new_sink_storage.factory_address = factory.address
            new_sink_storage.burn = {}
            new_sink_storage.exchanges = {}
            new_sink_storage.reserve = {}
            new_sink_storage.token_type_smak = {"fa12": smak_token.address}
            new_sink = Env().deploy_sink(init_storage=new_sink_storage)
            update_sink_params = {
                "number_of_pools": 1,
                "first_pool": 0,
                "new_sink_address": new_sink.address,
            }
            factory.updateSinkAddress(update_sink_params).send(**send_conf)
            self.assertEqual(
                factory.storage["default_sink"](), new_sink.address)
            self.assertEqual(dex.storage["sink"](), new_sink.address)
            self.assertEqual(
                new_sink.storage["exchanges"][
                    {"xtz": None}, {"fa2": (token_b.address, 0)}
                ](),
                dex_address,
            )

        def test02_it_updates_sink_address_multiple_exchanges(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(ALICE_PK)
            tokens = []
            pairs = []
            fa12_init_storage = FA12Storage()
            for token_info in default_token_info[:3]:
                decimals = int(token_info["decimals"].decode("utf-8"))
                token_metadata = {
                    0: {
                        "token_id": 0,
                        "token_info": token_info,
                    }
                }
                fa12_init_storage.token_metadata = token_metadata
                token = Env().deploy_fa12(fa12_init_storage)
                token = {
                    "token_type": {"fa12": token.address},
                    "address": token.address,
                    "decimals": decimals,
                }
                tokens.append(token)
            fa2_init_storage = FA2Storage()
            for token_info in default_token_info[3:]:
                decimals = int(token_info["decimals"].decode("utf-8"))
                token_metadata = {
                    0: {
                        "token_id": 0,
                        "token_info": token_info,
                    }
                }
                fa2_init_storage.token_metadata = token_metadata
                token = Env().deploy_fa2(fa2_init_storage)
                token = {
                    "token_type": {"fa2": (token.address, 0)},
                    "address": token.address,
                    "decimals": decimals,
                }
                tokens.append(token)
            for i, token_a in enumerate(tokens[:]):
                decimals_a = token_a["decimals"]
                address_a = token_a["address"]
                amount_a = int(1000 * math.pow(10, decimals_a))
                amount_type_a = {"amount": amount_a}
                if token_a["token_type"] == {"fa12": address_a}:
                    pytezos.contract(address_a).mint(
                        {"address": ALICE_PK, "value": amount_a}
                    ).send(**send_conf)
                    pytezos.contract(address_a).approve(
                        {"spender": factory.address, "value": amount_a}
                    ).send(**send_conf)
                else:
                    pytezos.contract(address_a).mint(
                        {
                            "address": ALICE_PK,
                            "amount": amount_a,
                            "metadata": {},
                            "token_id": 0,
                        }
                    ).send(**send_conf)
                    pytezos.contract(address_a).update_operators(
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
                amount_b = amount_a
                amount_type_b = {"mutez": amount_b}
                launch_exchange_params = {
                    "token_type_a": token_a["token_type"],
                    "token_type_b": {"xtz": None},
                    "token_amount_a": amount_type_a,
                    "token_amount_b": amount_type_b,
                    "curve": "product",
                    "metadata": lp_metadata,
                    "token_metadata": lp_token_metadata,
                }
                factory.launchExchange(launch_exchange_params).with_amount(
                    amount_b
                ).send(**send_conf)

                for token_b in tokens[i + 1:]:
                    decimals_b = token_a["decimals"]
                    address_b = token_b["address"]
                    amount_b = int(1000 * math.pow(10, decimals_b))
                    amount_type_b = {"amount": amount_b}
                    if token_a["token_type"] == {"fa12": address_a}:
                        pytezos.contract(address_a).mint(
                            {"address": ALICE_PK, "value": amount_a}
                        ).send(**send_conf)
                        pytezos.contract(address_a).approve(
                            {"spender": factory.address, "value": amount_a}
                        ).send(**send_conf)
                    else:
                        pytezos.contract(address_a).mint(
                            {
                                "address": ALICE_PK,
                                "amount": amount_a,
                                "metadata": {},
                                "token_id": 0,
                            }
                        ).send(**send_conf)
                        pytezos.contract(address_a).update_operators(
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
                    if token_b["token_type"] == {"fa12": address_b}:
                        pytezos.contract(address_b).mint(
                            {"address": ALICE_PK, "value": amount_b}
                        ).send(**send_conf)
                        pytezos.contract(address_b).approve(
                            {"spender": factory.address, "value": amount_b}
                        ).send(**send_conf)
                    else:
                        pytezos.contract(address_b).mint(
                            {
                                "address": ALICE_PK,
                                "amount": amount_b,
                                "metadata": {},
                                "token_id": 0,
                            }
                        ).send(**send_conf)
                        pytezos.contract(
                            token_b["token_type"]["fa2"][0]
                        ).update_operators(
                            [
                                {
                                    "add_operator": {
                                        "owner": ALICE_PK,
                                        "operator": factory.address,
                                        "token_id": 0,
                                    }
                                }
                            ]
                        ).send(
                            **send_conf
                        )
                    launch_exchange_params = {
                        "token_type_a": token_a["token_type"],
                        "token_type_b": token_b["token_type"],
                        "token_amount_a": amount_type_a,
                        "token_amount_b": amount_type_b,
                        "curve": "product",
                        "metadata": lp_metadata,
                        "token_metadata": lp_token_metadata,
                    }
                    factory.launchExchange(
                        launch_exchange_params).send(**send_conf)
                    pairs.append(
                        (token_a["token_type"], token_b["token_type"]))

            new_sink_storage = SinkStorage
            new_sink_storage.factory_address = factory.address
            new_sink_storage.burn = {}
            new_sink_storage.exchanges = {}
            new_sink_storage.reserve = {}
            new_sink_storage.token_type_smak = {"fa12": smak_token.address}
            new_sink = Env().deploy_sink(init_storage=new_sink_storage)
            number_of_pools = factory.storage["counter"]()
            update_sink_params = {
                "number_of_pools": number_of_pools,
                "first_pool": 0,
                "new_sink_address": new_sink.address,
            }
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            factory.updateSinkAddress(update_sink_params).send(**send_conf)

            for pair in pairs:
                dex_address = factory.storage["pairs"][pair]()
                dex = pytezos.using(**Env().using_params).contract(dex_address)
                self.assertEqual(dex.storage["sink"](), new_sink.address)
                self.assertEqual(
                    new_sink.storage["exchanges"][pair](), dex_address)

        def test_03_it_fails_when_counter_is_outside_pool_limit(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_address = factory.storage["pairs"][
                ({"xtz": None}, {"fa2": (token_b.address, 0)})
            ]()
            dex = pytezos.contract(dex_address).using(**Env().using_params)
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            self.assertEqual(dex.storage["sink"](), sink.address)
            new_sink_storage = SinkStorage
            new_sink_storage.factory_address = factory.address
            new_sink_storage.burn = {}
            new_sink_storage.exchanges = {}
            new_sink_storage.reserve = {}
            new_sink_storage.token_type_smak = {"fa12": smak_token.address}
            new_sink = Env().deploy_sink(init_storage=new_sink_storage)
            update_sink_params = {
                "number_of_pools": 2,
                "first_pool": 0,
                "new_sink_address": new_sink.address,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.updateSinkAddress(update_sink_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "130"})

        def test04_it_fails_when_new_sink_has_no_add_exchange_entrypoint(self):
            factory, _, sink, multisig = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_address = factory.storage["pairs"][
                ({"xtz": None}, {"fa2": (token_b.address, 0)})
            ]()
            dex = pytezos.contract(dex_address).using(**Env().using_params)
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            self.assertEqual(dex.storage["sink"](), sink.address)
            update_sink_params = {
                "number_of_pools": 1,
                "first_pool": 0,
                "new_sink_address": multisig.address,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.updateSinkAddress(update_sink_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "124"})

        def test05_it_fails_when_caller_is_not_an_admin(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_address = factory.storage["pairs"][
                ({"xtz": None}, {"fa2": (token_b.address, 0)})
            ]()
            dex = pytezos.contract(dex_address).using(**Env().using_params)
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            self.assertEqual(dex.storage["sink"](), sink.address)
            new_sink_storage = SinkStorage
            new_sink_storage.factory_address = factory.address
            new_sink_storage.burn = {}
            new_sink_storage.exchanges = {}
            new_sink_storage.reserve = {}
            new_sink_storage.token_type_smak = {"fa12": smak_token.address}
            new_sink = Env().deploy_sink(init_storage=new_sink_storage)
            update_sink_params = {
                "number_of_pools": 1,
                "first_pool": 0,
                "new_sink_address": new_sink.address,
            }
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(factory.address).updateSinkAddress(
                    update_sink_params
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1001"})

        def test06_it_fails_when_factory_is_not_authorized_by_multisig(self):
            factory, smak_token, sink, multisig = Env().deploy_full_app(ALICE_PK)
            multisig.removeAuthorizedContract(
                factory.address).send(**send_conf)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_address = factory.storage["pairs"][
                ({"xtz": None}, {"fa2": (token_b.address, 0)})
            ]()
            dex = pytezos.contract(dex_address).using(**Env().using_params)
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            self.assertEqual(dex.storage["sink"](), sink.address)
            new_sink_storage = SinkStorage
            new_sink_storage.factory_address = factory.address
            new_sink_storage.burn = {}
            new_sink_storage.exchanges = {}
            new_sink_storage.reserve = {}
            new_sink_storage.token_type_smak = {"fa12": smak_token.address}
            new_sink = Env().deploy_sink(init_storage=new_sink_storage)
            update_sink_params = {
                "number_of_pools": 1,
                "first_pool": 0,
                "new_sink_address": new_sink.address,
            }
            with self.assertRaises(MichelsonError) as err:
                factory.updateSinkAddress(update_sink_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1009"})

        def test07_it_fails_when_alice_votes_twice(self):
            factory, smak_token, sink, multisig = Env().deploy_full_app(ALICE_PK)
            token_b = Env().deploy_fa2(FA2Storage())
            token_b.mint(
                {"address": ALICE_PK, "amount": 10 **
                    6, "metadata": {}, "token_id": 0}
            ).send(**send_conf)
            token_b.update_operators(
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
            launch_exchange_params = {
                "token_type_a": {"xtz": None},
                "token_type_b": {"fa2": (token_b.address, 0)},
                "token_amount_a": {"mutez": 10**6},
                "token_amount_b": {"amount": 10**6},
                "curve": "product",
                "metadata": lp_metadata,
                "token_metadata": lp_token_metadata,
            }
            factory.launchExchange(launch_exchange_params).with_amount(10**6).send(
                **send_conf
            )
            dex_address = factory.storage["pairs"][
                ({"xtz": None}, {"fa2": (token_b.address, 0)})
            ]()
            dex = pytezos.contract(dex_address).using(**Env().using_params)
            self.assertEqual(factory.storage["default_sink"](), sink.address)
            self.assertEqual(dex.storage["sink"](), sink.address)
            new_sink_storage = SinkStorage
            new_sink_storage.factory_address = factory.address
            new_sink_storage.burn = {}
            new_sink_storage.exchanges = {}
            new_sink_storage.reserve = {}
            new_sink_storage.token_type_smak = {"fa12": smak_token.address}
            new_sink = Env().deploy_sink(init_storage=new_sink_storage)
            update_sink_params = {
                "number_of_pools": 1,
                "first_pool": 0,
                "new_sink_address": new_sink.address,
            }
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            factory.updateSinkAddress(update_sink_params).send(**send_conf)
            with self.assertRaises(MichelsonError) as err:
                factory.updateSinkAddress(update_sink_params).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1008"})

    def test_inner_test_class(self):
        test_classes_to_run = [
            self.LaunchExchange,
            self.RemoveExchange,
            self.LaunchSink,
            self.SetLqtAddress,
            self.SetSinkClaimLimit,
            self.UpdateBaker,
            self.UpdateMultisig,
            self.UpdateSinkAddress,
        ]
        suites_list = []
        for test_class in test_classes_to_run:
            suites_list.append(
                unittest.TestLoader().loadTestsFromTestCase(test_class))

        big_suite = unittest.TestSuite(suites_list)
        unittest.TextTestRunner().run(big_suite)


if __name__ == "__main__":
    unittest.main()
