import unittest
import logging
from pytezos.rpc.errors import MichelsonError
from env import (
    Env,
    ALICE_PK,
    pytezos,
    FA12Storage,
    FA2Storage,
    send_conf,
    _using_params,
    bob_pytezos,
    BOB_PK,
    metadata,
    token_metadata,
    DEFAULT_BAKER,
)

logging.basicConfig(level=logging.INFO)


class TestSink(unittest.TestCase):
    @staticmethod
    def print_title(instance):
        print("Test Sink: " + instance.__class__.__name__ + "...")
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

    class Claim(unittest.TestCase):
        def test0_before_tests(self):
            TestSink.print_title(self)

        def test01_claim_multiple(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            pairs = []
            dexs = []
            tokens = []
            for i in range(1):
                token_a = Env().deploy_fa2(FA2Storage())
                token_a_type = {"fa2": (token_a.address, 0)}
                tokens.append(token_a_type)
                for j in range(4):
                    token_b = Env().deploy_fa2(FA2Storage())
                    token_b_type = {"fa2": (token_b.address, 0)}
                    token_a.mint(
                        {
                            "address": ALICE_PK,
                            "amount": 10**10,
                            "metadata": {},
                            "token_id": 0,
                        }
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
                            "amount": 10**10,
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
                        "token_type_a": token_a_type,
                        "token_type_b": token_b_type,
                        "token_amount_a": {"amount": 10**10},
                        "token_amount_b": {"amount": 10**10},
                        "curve": "product",
                        "metadata": metadata,
                        "token_metadata": token_metadata,
                    }
                    factory.launchExchange(
                        launch_exchange_params).send(**send_conf)
                    dex = factory.storage["pairs"][(
                        token_a_type, token_b_type)]()
                    pairs.append((token_a_type, token_b_type))
                    dexs.append(dex)
                    tokens.append(token_b_type)

            for token in tokens:
                token_addr = token["fa2"][0]
                token_a = pytezos.contract(token_addr).using(**_using_params)
                token_a.mint(
                    {
                        "address": ALICE_PK,
                        "amount": 10**10,
                        "metadata": {},
                        "token_id": 0,
                    }
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
                smak_token.mint({"address": ALICE_PK, "value": 10**10}).send(
                    **send_conf
                )
                smak_token.approve(
                    {"spender": factory.address, "value": 10**10}
                ).send(**send_conf)
                launch_exchange_params = {
                    "token_type_a": token,
                    "token_type_b": {"fa12": smak_token.address},
                    "token_amount_a": {"amount": 10**10},
                    "token_amount_b": {"amount": 10**10},
                    "curve": "product",
                    "metadata": metadata,
                    "token_metadata": token_metadata,
                }
                factory.launchExchange(
                    launch_exchange_params).send(**send_conf)

            for pair in pairs:
                token_a_type = pair[0]
                token_b_type = pair[1]
                token_a_address = token_a_type["fa2"][0]
                token_b_address = token_b_type["fa2"][0]
                token_a = pytezos.contract(
                    token_a_address).using(**_using_params)
                token_b = pytezos.contract(
                    token_b_address).using(**_using_params)

                dex_addr = factory.storage["pairs"][pair]()
                token_a.mint(
                    {
                        "address": ALICE_PK,
                        "amount": 2 * 10**5,
                        "metadata": {},
                        "token_id": 0,
                    }
                ).send(**send_conf)
                token_a.update_operators(
                    [
                        {
                            "add_operator": {
                                "owner": ALICE_PK,
                                "operator": dex_addr,
                                "token_id": 0,
                            }
                        }
                    ]
                ).send(**send_conf)
                token_b.mint(
                    {
                        "address": ALICE_PK,
                        "amount": 2 * 10**5,
                        "metadata": {},
                        "token_id": 0,
                    }
                ).send(**send_conf)
                token_b.update_operators(
                    [
                        {
                            "add_operator": {
                                "owner": ALICE_PK,
                                "operator": dex_addr,
                                "token_id": 0,
                            }
                        }
                    ]
                ).send(**send_conf)
                dex = pytezos.contract(dex_addr).using(**_using_params)
                dex.swap(
                    {
                        "t2t_to": ALICE_PK,
                        "tokens_sold": 10**5,
                        "min_tokens_bought": 0,
                        "a_to_b": True,
                        "deadline": pytezos.now() + 10**3,
                    }
                ).send(**send_conf)

                burn_amount = 10**5 * 2 // 10**4
                reserve_amount = 10**5 // 10**4
                # self.assertEqual(
                #     sink.storage["burn"][token_a_type](), burn_amount)
                # self.assertEqual(
                #     sink.storage["reserve"][token_a_type](), reserve_amount
                # )

                dex.swap(
                    {
                        "t2t_to": ALICE_PK,
                        "tokens_sold": 10**5,
                        "min_tokens_bought": 0,
                        "a_to_b": False,
                        "deadline": pytezos.now() + 10**3,
                    }
                ).send(**send_conf)
                # self.assertEqual(
                #     sink.storage["burn"][token_b_type](), burn_amount)
                # self.assertEqual(
                #     sink.storage["reserve"][token_b_type](), reserve_amount
                # )

            bob_pytezos.contract(sink.address).claim(
                {
                    "tokens": tokens,
                    "deadline": pytezos.now() + 10**6,
                    "reward_to": ALICE_PK,
                }
            ).send(**send_conf)

        def test02_claim_multiple_fa12(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            pairs = []
            dexs = []
            tokens = []

            for i in range(1):
                token_a = Env().deploy_fa12(FA12Storage())
                token_a_type = {"fa12": token_a.address}
                tokens.append(token_a_type)
                for j in range(10):
                    token_b = Env().deploy_fa12(FA12Storage())
                    token_b_type = {"fa12": token_b.address}
                    token_a.mint({"address": ALICE_PK, "value": 10**10}).send(
                        **send_conf
                    )
                    token_a.approve(
                        {"spender": factory.address, "value": 10**10}
                    ).send(**send_conf)
                    token_b.mint({"address": ALICE_PK, "value": 10**10}).send(
                        **send_conf
                    )
                    token_b.approve(
                        {"spender": factory.address, "value": 10**10}
                    ).send(**send_conf)
                    launch_exchange_params = {
                        "token_type_a": token_a_type,
                        "token_type_b": token_b_type,
                        "token_amount_a": {"amount": 10**10},
                        "token_amount_b": {"amount": 10**10},
                        "curve": "product",
                        "metadata": metadata,
                        "token_metadata": token_metadata,
                    }
                    factory.launchExchange(
                        launch_exchange_params).send(**send_conf)
                    dex = factory.storage["pairs"][(
                        token_a_type, token_b_type)]()
                    pairs.append((token_a_type, token_b_type))
                    dexs.append(dex)
                    tokens.append(token_b_type)

                for token in tokens:
                    token_addr = token["fa12"]
                    token_a = pytezos.contract(
                        token_addr).using(**_using_params)
                    token_a.mint({"address": ALICE_PK, "value": 10**10}).send(
                        **send_conf
                    )
                    token_a.approve(
                        {"spender": factory.address, "value": 10**10}
                    ).send(**send_conf)
                    smak_token.mint({"address": ALICE_PK, "value": 10**10}).send(
                        **send_conf
                    )
                    smak_token.approve(
                        {"spender": factory.address, "value": 10**10}
                    ).send(**send_conf)
                    launch_exchange_params = {
                        "token_type_a": token,
                        "token_type_b": {"fa12": smak_token.address},
                        "token_amount_a": {"amount": 10**10},
                        "token_amount_b": {"amount": 10**10},
                        "curve": "product",
                        "metadata": metadata,
                        "token_metadata": token_metadata,
                    }
                    factory.launchExchange(
                        launch_exchange_params).send(**send_conf)

                for pair in pairs:
                    token_a_type = pair[0]
                    token_b_type = pair[1]
                    token_a_address = token_a_type["fa12"]
                    token_b_address = token_b_type["fa12"]
                    token_a = pytezos.contract(
                        token_a_address).using(**_using_params)
                    token_b = pytezos.contract(
                        token_b_address).using(**_using_params)

                    dex_addr = factory.storage["pairs"][pair]()
                    token_a.mint({"address": ALICE_PK, "value": 2 * 10**5}).send(
                        **send_conf
                    )
                    token_a.approve({"spender": dex_addr, "value": 2 * 10**5}).send(
                        **send_conf
                    )
                    token_b.mint({"address": ALICE_PK, "value": 2 * 10**5}).send(
                        **send_conf
                    )
                    token_b.approve({"spender": dex_addr, "value": 2 * 10**5}).send(
                        **send_conf
                    )
                    dex = pytezos.contract(dex_addr).using(**_using_params)
                    dex.swap(
                        {
                            "t2t_to": ALICE_PK,
                            "tokens_sold": 10**5,
                            "min_tokens_bought": 0,
                            "a_to_b": True,
                            "deadline": pytezos.now() + 10**3,
                        }
                    ).send(**send_conf)

                    dex.swap(
                        {
                            "t2t_to": ALICE_PK,
                            "tokens_sold": 10**5,
                            "min_tokens_bought": 0,
                            "a_to_b": False,
                            "deadline": pytezos.now() + 10**3,
                        }
                    ).send(**send_conf)

                bob_pytezos.contract(sink.address).claim(
                    {
                        "tokens": tokens,
                        "deadline": pytezos.now() + 10**6,
                        "reward_to": ALICE_PK,
                    }
                ).send(**send_conf)

        def test03_sink_claim_reward(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            token_a.mint({"address": ALICE_PK, "value": 2 * 10**12 + 10**10}).send(
                **send_conf
            )
            token_a.approve({"spender": factory.address, "value": 2 * 10**12}).send(
                **send_conf
            )
            token_b.mint({"address": ALICE_PK, "value": 10**12}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            smak_token.mint(
                {"address": ALICE_PK, "value": 10**12}).send(**send_conf)
            smak_token.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": smak_token.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_addr = factory.storage["pairs"][
                ({"fa12": token_a.address}, {"fa12": token_b.address})
            ]()
            dex = pytezos.contract(dex_addr).using(**_using_params)
            token_a.approve({"spender": dex.address, "value": 10**10}).send(
                **send_conf
            )
            dex.swap(
                {
                    "t2t_to": ALICE_PK,
                    "tokens_sold": 10**10,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10**3,
                }
            ).send(**send_conf)

            burn_amount = 10**10 * 2 // 10**4
            reserve_amount = 10**10 // 10**4
            reserve_address = sink.storage["reserve_address"]()

            tokens_in = burn_amount * 9972 // 10**4
            bought = (tokens_in * 10**12) // (10**12 + tokens_in)

            bob_pytezos.contract(sink.address).claim(
                {
                    "tokens": [{"fa12": token_a.address}],
                    "deadline": pytezos.now() + 10**6,
                    "reward_to": BOB_PK,
                }
            ).send(**send_conf)
            self.assertEqual(
                token_a.storage["tokens"][reserve_address](), reserve_amount
            )

        def test04_it_fails_when_token_list_is_empty(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            token_a.mint({"address": ALICE_PK, "value": 2 * 10**12 + 10**10}).send(
                **send_conf
            )
            token_a.approve({"spender": factory.address, "value": 2 * 10**12}).send(
                **send_conf
            )
            token_b.mint({"address": ALICE_PK, "value": 10**12}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            smak_token.mint(
                {"address": ALICE_PK, "value": 10**12}).send(**send_conf)
            smak_token.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": smak_token.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_addr = factory.storage["pairs"][
                ({"fa12": token_a.address}, {"fa12": token_b.address})
            ]()
            dex = pytezos.contract(dex_addr).using(**_using_params)
            token_a.approve({"spender": dex.address, "value": 10**10}).send(
                **send_conf
            )
            dex.swap(
                {
                    "t2t_to": ALICE_PK,
                    "tokens_sold": 10**10,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10**3,
                }
            ).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(sink.address).claim(
                    {
                        "tokens": [],
                        "deadline": pytezos.now() + 10**6,
                        "reward_to": BOB_PK,
                    }
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "324"})

        def test05_it_fails_when_token_list_is_too_large(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            token_a.mint({"address": ALICE_PK, "value": 2 * 10**12 + 10**10}).send(
                **send_conf
            )
            token_a.approve({"spender": factory.address, "value": 2 * 10**12}).send(
                **send_conf
            )
            token_b.mint({"address": ALICE_PK, "value": 10**12}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            smak_token.mint(
                {"address": ALICE_PK, "value": 10**12}).send(**send_conf)
            smak_token.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": smak_token.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_addr = factory.storage["pairs"][
                ({"fa12": token_a.address}, {"fa12": token_b.address})
            ]()
            dex = pytezos.contract(dex_addr).using(**_using_params)
            token_a.approve({"spender": dex.address, "value": 10**10}).send(
                **send_conf
            )
            dex.swap(
                {
                    "t2t_to": ALICE_PK,
                    "tokens_sold": 10**10,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10**3,
                }
            ).send(**send_conf)
            factory.setSinkClaimLimit(0).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(sink.address).claim(
                    {
                        "tokens": [{"fa12": token_a.address}],
                        "deadline": pytezos.now() + 10**6,
                        "reward_to": BOB_PK,
                    }
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "317"})

        def test06_it_fails_when_no_token_to_smak_dex_exists(self):
            factory, _, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            token_a.mint({"address": ALICE_PK, "value": 2 * 10**12 + 10**10}).send(
                **send_conf
            )
            token_a.approve({"spender": factory.address, "value": 2 * 10**12}).send(
                **send_conf
            )
            token_b.mint({"address": ALICE_PK, "value": 10**12}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_addr = factory.storage["pairs"][
                ({"fa12": token_a.address}, {"fa12": token_b.address})
            ]()
            dex = pytezos.contract(dex_addr).using(**_using_params)
            token_a.approve({"spender": dex.address, "value": 10**10}).send(
                **send_conf
            )
            dex.swap(
                {
                    "t2t_to": ALICE_PK,
                    "tokens_sold": 10**10,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10**3,
                }
            ).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(sink.address).claim(
                    {
                        "tokens": [{"fa12": token_a.address}],
                        "deadline": pytezos.now() + 10**6,
                        "reward_to": BOB_PK,
                    }
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "320"})

        def test07_it_fails_when_token_to_burn_not_listed(self):
            factory, smak_token, sink, _ = Env().deploy_full_app(DEFAULT_BAKER)
            token_a = Env().deploy_fa12(FA12Storage())
            token_b = Env().deploy_fa12(FA12Storage())
            token_a.mint({"address": ALICE_PK, "value": 10**12 + 10**10}).send(
                **send_conf
            )
            token_a.approve({"spender": factory.address, "value": 2 * 10**12}).send(
                **send_conf
            )
            token_b.mint({"address": ALICE_PK, "value": 2 * 10**12}
                         ).send(**send_conf)
            token_b.approve({"spender": factory.address, "value": 2 * 10**12}).send(
                **send_conf
            )
            smak_token.mint(
                {"address": ALICE_PK, "value": 10**12}).send(**send_conf)
            smak_token.approve({"spender": factory.address, "value": 10**12}).send(
                **send_conf
            )
            launch_exchange_params = {
                "token_type_a": {"fa12": token_b.address},
                "token_type_b": {"fa12": smak_token.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            launch_exchange_params = {
                "token_type_a": {"fa12": token_a.address},
                "token_type_b": {"fa12": token_b.address},
                "token_amount_a": {"amount": 10**12},
                "token_amount_b": {"amount": 10**12},
                "curve": "product",
                "metadata": metadata,
                "token_metadata": token_metadata,
            }
            factory.launchExchange(launch_exchange_params).send(**send_conf)
            dex_addr = factory.storage["pairs"][
                ({"fa12": token_a.address}, {"fa12": token_b.address})
            ]()
            dex = pytezos.contract(dex_addr).using(**_using_params)
            token_a.approve({"spender": dex.address, "value": 10**10}).send(
                **send_conf
            )
            dex.swap(
                {
                    "t2t_to": ALICE_PK,
                    "tokens_sold": 10**10,
                    "min_tokens_bought": 0,
                    "a_to_b": True,
                    "deadline": pytezos.now() + 10**3,
                }
            ).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(sink.address).claim(
                    {
                        "tokens": [{"fa12": token_b.address}],
                        "deadline": pytezos.now() + 10**6,
                        "reward_to": BOB_PK,
                    }
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "313"})

    def test_inner_test_class(self):
        test_classes_to_run = [
            self.Claim,
        ]
        suites_list = []
        for test_class in test_classes_to_run:
            suites_list.append(
                unittest.TestLoader().loadTestsFromTestCase(test_class))

        big_suite = unittest.TestSuite(suites_list)
        unittest.TextTestRunner().run(big_suite)


if __name__ == "__main__":
    unittest.main()
