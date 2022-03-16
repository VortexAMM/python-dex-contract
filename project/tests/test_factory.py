from test_env import Env, ALICE_PK, pytezos, FA12Storage, FA2Storage, FactoryStorage, LqtStorage, send_conf
from data import default_token_info
from unittest import TestCase
import math
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult


class Factory:
    launch_exchange_params = {
        "token_type_a": {},
        "token_type_b": {},
        "token_amount_a": 0,
        "token_amount_b": 0,
        "curve": "product",
        "lp_address": ALICE_PK,
    }


class TestFactory(TestCase):
    @staticmethod
    def print_title(instance):
        print("Test Factory: " + instance.__class__.__name__ + "...")
        print("-----------------------------------")

    @staticmethod
    def print_success(function_name):
        print(function_name + "... ok")
        print("-----------------------------------")

    # class LaunchExchange(TestCase):
    def test0_before_tests(self):
        TestFactory.print_title(self)

    def test1_it_launches_exchange(self):
        factory, _, _ = Env().deploy_full_app()
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
            token = {"token_type": {
                "fa12": token.address}, "address": token.address, "decimals": decimals}
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
            token = {"token_type": {
                "fa2": (token.address, 0)}, "address": token.address, "decimals": decimals}
            tokens.append(token)
        for i, token_a in enumerate(tokens[:]):
            liquidity_token = Env().deploy_liquidity_token(LqtStorage())
            decimals_a = token_a["decimals"]
            address_a = token_a["address"]
            amount_a = int(1000 * math.pow(10, decimals_a))
            amount_type_a = {"amount": amount_a}
            if token_a["token_type"] == {"fa12": address_a}:
                pytezos.contract(address_a).mint(
                    {"address": ALICE_PK, "value": amount_a}).send(**send_conf)
                pytezos.contract(address_a).approve({"spender": factory.address,
                                                     "value": amount_a}).send(**send_conf)
            else:
                pytezos.contract(address_a).mint({"address": ALICE_PK, "amount": amount_a,
                                                  "metadata": {}, "token_id": 0}).send(**send_conf)
                pytezos.contract(address_a).update_operators([{"add_operator": {
                    "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
            amount_b = amount_a
            amount_type_b = {"mutez": None}
            launch_exchange_params = Factory.launch_exchange_params
            launch_exchange_params["token_amount_a"] = amount_type_a
            launch_exchange_params["token_amount_b"] = amount_type_b
            launch_exchange_params["token_type_a"] = token_a["token_type"]
            launch_exchange_params["token_type_b"] = {"xtz": None}
            launch_exchange_params["lp_address"] = liquidity_token.address
            opg = factory.launchExchange(
                launch_exchange_params).with_amount(amount_b).send(**send_conf)
            consumed_gas = OperationResult.consumed_gas(opg.opg_result)
            write_type_a = "fa1.2" if token_a["token_type"] == {
                "fa12": address_a} else "fa2"
            with open('launch_exchange.txt', 'a') as f:
                f.write(
                    f'token a: {write_type_a} {address_a} ; token b: XTZ ; {consumed_gas} gas \n')
            for token_b in tokens[i + 1:]:
                decimals_b = token_a["decimals"]
                address_b = token_b["address"]
                amount_b = int(1000 * math.pow(10, decimals_b))
                amount_type_b = {"amount": amount_b}
                if token_a["token_type"] == {"fa12": address_a}:
                    pytezos.contract(address_a).mint(
                        {"address": ALICE_PK, "value": amount_a}).send(**send_conf)
                    pytezos.contract(address_a).approve({"spender": factory.address,
                                                         "value": amount_a}).send(**send_conf)
                else:
                    pytezos.contract(address_a).mint({"address": ALICE_PK, "amount": amount_a,
                                                      "metadata": {}, "token_id": 0}).send(**send_conf)
                    pytezos.contract(address_a).update_operators([{"add_operator": {
                        "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
                if token_b["token_type"] == {"fa12": address_b}:
                    pytezos.contract(address_b).mint(
                        {"address": ALICE_PK, "value": amount_b}).send(**send_conf)
                    pytezos.contract(address_b).approve({"spender": factory.address,
                                                         "value": amount_b}).send(**send_conf)
                else:
                    pytezos.contract(address_b).mint({"address": ALICE_PK, "amount": amount_b,
                                                      "metadata": {}, "token_id": 0}).send(**send_conf)
                    pytezos.contract(token_b["token_type"]["fa2"][0]).update_operators([{"add_operator": {
                        "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
                launch_exchange_params = Factory.launch_exchange_params
                launch_exchange_params["token_amount_a"] = amount_type_a
                launch_exchange_params["token_amount_b"] = amount_type_b
                launch_exchange_params["token_type_a"] = token_a["token_type"]
                launch_exchange_params["token_type_b"] = token_b["token_type"]
                opg = factory.launchExchange(
                    launch_exchange_params).send(**send_conf)
                consumed_gas = OperationResult.consumed_gas(opg.opg_result)

                write_type_b = "fa1.2" if token_b["token_type"] == {
                    "fa12": address_b} else "fa2"

                with open('launch_exchange.txt', 'a') as f:
                    f.write(
                        f'token a: {write_type_a} {address_a} ; token b: {write_type_b} {address_b} ; {consumed_gas} gas \n')
        TestFactory.print_success("test1_it_launches_exchange")

    def test2_it_fails_when_sink_is_not_deployed(self):
        init_storage = FactoryStorage()
        factory = Env().deploy_factory(init_storage)
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_b"] = {"amount": 10 ** 6}
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "104"})
        TestFactory.print_success(
            "test2_it_fails_when_sink_is_not_deployed")

    def test3_it_fails_when_tokens_are_equal_fa12(self):
        factory, smak_token, sink = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_b"] = {"amount": 10 ** 6}
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_a.address}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "101"})
        TestFactory.print_success(
            "test3_it_fails_when_tokens_are_equal_fa12")

    def test4_it_fails_when_tokens_are_equal_fa2(self):
        factory, smak_token, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_a = Env().deploy_fa2(fa2_init_storage)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_b"] = {"amount": 10 ** 6}
        launch_exchange_params["token_type_a"] = {
            "fa2": (token_a.address, 0)}
        launch_exchange_params["token_type_b"] = {
            "fa2": (token_a.address, 0)}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "101"})
        TestFactory.print_success(
            "test4_it_fails_when_tokens_are_equal_fa2")

    def test5_it_fails_when_tokens_are_equal_xtz(self):
        factory, smak_token, sink = Env().deploy_full_app()
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        launch_exchange_params["token_amount_b"] = {"mutez": None}
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {"xtz": None}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(launch_exchange_params).with_amount(
                10 ** 6).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "101"})
        TestFactory.print_success(
            "test5_it_fails_when_tokens_are_equal_xtz")

    def test6_it_fails_when_pair_already_exists(self):
        factory, smak_token, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_a = Env().deploy_fa2(fa2_init_storage)
        token_a.mint({"address": ALICE_PK, "amount": 10 ** 6,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_a.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        fa12_init_storage = FA12Storage()
        token_b = Env().deploy_fa12(fa12_init_storage)
        token_b.mint(
            {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
        token_b.approve({"spender": factory.address,
                         "value": 10 ** 6}).send(**send_conf)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_type_a"] = {
            "fa2": (token_a.address, 0)}
        launch_exchange_params["token_amount_b"] = {"amount": 10 ** 6}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        token_a.mint({"address": ALICE_PK, "amount": 10 ** 6,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_a.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        token_b.mint(
            {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
        token_b.approve({"spender": factory.address,
                         "value": 10 ** 6}).send(**send_conf)
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "102"})
        # also in reverse order
        launch_exchange_params["token_type_b"] = {
            "fa2": (token_a.address, 0)}
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_b"] = {"amount": 10 ** 6}
        launch_exchange_params["token_type_a"] = {"fa12": token_b.address}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "102"})
        TestFactory.print_success(
            "test6_it_fails_when_pair_already_exists")

    def test7_it_fails_when_pools_are_empty_fa12(self):
        factory, smak_token, sink = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        token_a.mint(
            {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
        token_a.approve({"spender": factory.address,
                         "value": 10 ** 6}).send(**send_conf)
        token_b.mint(
            {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
        token_b.approve({"spender": factory.address,
                         "value": 10 ** 6}).send(**send_conf)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_b"] = {"amount": 0}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "103"})
        TestFactory.print_success(
            "test7_it_fails_when_pools_are_empty_fa12")

    def test8_it_fails_when_pools_are_empty_fa2(self):
        factory, smak_token, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_a = Env().deploy_fa2(fa2_init_storage)
        token_b = Env().deploy_fa2(fa2_init_storage)
        token_a.mint({"address": ALICE_PK, "amount": 10 ** 6,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_a.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "amount": 10 ** 6,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_b.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {
            "fa2": (token_a.address, 0)}
        launch_exchange_params["token_type_b"] = {
            "fa2": (token_b.address, 0)}
        launch_exchange_params["token_amount_a"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_b"] = {"amount": 0}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "103"})
        TestFactory.print_success(
            "test8_it_fails_when_pools_are_empty_fa2")

    def test9_it_fails_when_pools_are_empty_xtz(self):
        factory, smak_token, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_b = Env().deploy_fa2(fa2_init_storage)
        token_b.mint({"address": ALICE_PK, "amount": 10 ** 6,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_b.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {
            "fa2": (token_b.address, 0)}
        launch_exchange_params["token_amount_b"] = {"amount": 10 ** 6}
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        with self.assertRaises(MichelsonError) as err:
            factory.launchExchange(
                launch_exchange_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "103"})
        TestFactory.print_success(
            "test9_it_fails_when_pools_are_empty_xtz")
