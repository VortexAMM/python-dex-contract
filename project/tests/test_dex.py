from test_flat import newton
from test_env import Env, ALICE_PK, pytezos, FA12Storage, FA2Storage, FactoryStorage, LqtStorage, send_conf, _using_params, BOB_PK
from test_factory import Factory
from unittest import TestCase
from pytezos.rpc.errors import MichelsonError
from pytezos.contract.result import OperationResult


class Dex:
    add_liquidity_params = {
        "owner": ALICE_PK,
        "amount_token_a": 0,
        "min_lqt_minted": 0,
        "max_tokens_deposited": 0,
        "deadline": pytezos.now(),
    }

    remove_liquidity_params = {
        "rem_to": ALICE_PK,
        "lqt_burned": 0,
        "min_token_a_withdrawn": 0,
        "min_token_b_withdrawn": 0,
        "deadline": pytezos.now(),
    }

    set_baker_param = {
        "baker": ALICE_PK,
        "freeze_baker": False,
    }

    set_lqt_address_param = ALICE_PK

    swap_param = {
        "t2t_to": ALICE_PK,
        "tokens_sold": 0,
        "min_tokens_bought": 0,
        "a_to_b": True,
        "deadline": pytezos.now(),
    }

    update_reserve_param = ALICE_PK

    update_token_pool_param = None


class TestDex(TestCase):
    @staticmethod
    def print_title(instance):
        print("Test Factory: " + instance.__class__.__name__ + "...")
        print("-----------------------------------")

    @staticmethod
    def print_success(function_name):
        print(function_name + "... ok")
        print("-----------------------------------")

    # class AddLiquidity(TestCase):
    def test00_before_tests(self):
        TestDex.print_title(self)

    def test01_it_adds_liquidity_successfuly(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_address = dex.storage["lqt_address"]()
        lqt = pytezos.contract(lqt_address).using(**_using_params)
        alice_liquidity = lqt.storage["tokens"][ALICE_PK]()
        lqt_total = dex.storage["lqt_total"]()
        add_liquidity_params = Dex.add_liquidity_params
        add_amount_a = 10 ** 6
        add_liquidity_params["amount_token_a"] = add_amount_a
        add_liquidity_params["max_tokens_deposited"] = add_amount_a * \
            amount_b // amount_a
        token_a.mint({"address": ALICE_PK, "value": add_amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": dex.address,
                        "value": add_amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                     ).send(**send_conf)
        token_b.approve({"spender": dex.address,
                        "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
        add_liquidity_params["min_lqt_minted"] = add_amount_a * \
            lqt_total // amount_a
        add_liquidity_params["deadline"] = pytezos.now() + 100
        opg = dex.addLiquidity(add_liquidity_params).send(**send_conf)
        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        with open('../../add_liquidity_gas.txt', 'a') as f:
            f.write(
                f'new add_liquidity with no baker_rewards call : {consumed_gas} gas; \n')
        self.assertEqual(dex.storage["lqt_total"](
        ), lqt_total + add_amount_a * lqt_total // amount_a)
        self.assertEqual(dex.storage["token_pool_a"](
        ), add_amount_a + amount_a)
        self.assertEqual(dex.storage["token_pool_b"](
        ), amount_b + add_amount_a * amount_b // amount_a)
        self.assertEqual(dex.storage["last_k"](
        ), (add_amount_a + amount_a) * (amount_b + add_amount_a * amount_b // amount_a))
        self.assertEqual(lqt.storage["tokens"][ALICE_PK](
        ), alice_liquidity + add_amount_a * lqt_total // amount_a)

    def test_add_liquidity_gas_consumption_with_xtz(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).with_amount(
            amount_a).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"xtz": None}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_address = dex.storage["lqt_address"]()
        lqt = pytezos.contract(lqt_address).using(**_using_params)
        alice_liquidity = lqt.storage["tokens"][ALICE_PK]()
        lqt_total = dex.storage["lqt_total"]()
        add_liquidity_params = Dex.add_liquidity_params
        add_amount_a = 10 ** 6
        add_liquidity_params["amount_token_a"] = add_amount_a
        add_liquidity_params["max_tokens_deposited"] = add_amount_a * \
            amount_b // amount_a
        token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                     ).send(**send_conf)
        token_b.approve({"spender": dex.address,
                        "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
        add_liquidity_params["min_lqt_minted"] = add_amount_a * \
            lqt_total // amount_a
        add_liquidity_params["deadline"] = pytezos.now() + 100
        opg = dex.addLiquidity(add_liquidity_params).with_amount(
            add_amount_a).send(**send_conf)
        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        with open('../../add_liquidity_gas.txt', 'a') as f:
            f.write(
                f'new add_liquidity with baker_rewards call : {consumed_gas} gas; \n')

    def test02_it_fails_when_max_tokens_deposited_is_smaller_than_tokens_deposited(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        add_liquidity_params = Dex.add_liquidity_params
        add_amount_a = 10 ** 6
        add_liquidity_params["amount_token_a"] = add_amount_a
        token_a.mint({"address": ALICE_PK, "value": add_amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": dex.address,
                        "value": add_amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                     ).send(**send_conf)
        token_b.approve({"spender": dex.address,
                        "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
        add_liquidity_params["min_lqt_minted"] = add_amount_a * \
            lqt_total // amount_a
        add_liquidity_params["deadline"] = pytezos.now() + 100
        with self.assertRaises(MichelsonError) as err:
            add_liquidity_params["max_tokens_deposited"] = add_amount_a * \
                amount_b // amount_a - 1
            dex.addLiquidity(add_liquidity_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "203"})

    def test03_it_fails_when_lqt_minted_is_lesser_than_min_lqt_minted(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        add_liquidity_params = Dex.add_liquidity_params
        add_amount_a = 10 ** 6
        add_liquidity_params["amount_token_a"] = add_amount_a
        token_a.mint({"address": ALICE_PK, "value": add_amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": dex.address,
                        "value": add_amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": add_liquidity_params["max_tokens_deposited"]}
                     ).send(**send_conf)
        token_b.approve({"spender": dex.address,
                        "value": add_liquidity_params["max_tokens_deposited"]}).send(**send_conf)
        add_liquidity_params["max_tokens_deposited"] = add_amount_a * \
            amount_b // amount_a
        add_liquidity_params["deadline"] = pytezos.now() + 100
        with self.assertRaises(MichelsonError) as err:
            add_liquidity_params["min_lqt_minted"] = add_amount_a * \
                lqt_total // amount_a + 1
            dex.addLiquidity(add_liquidity_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "204"})

    def test10_it_removes_liquidity_successfuly(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        remove_amount = 10 ** 6
        remove_liquidity_params = Dex.remove_liquidity_params
        remove_liquidity_params["rem_to"] = ALICE_PK
        remove_liquidity_params["lqt_burned"] = remove_amount
        remove_liquidity_params["min_token_a_withdrawn"] = remove_amount * \
            amount_a // lqt_total
        remove_liquidity_params["min_token_b_withdrawn"] = remove_amount * \
            amount_b // lqt_total
        remove_liquidity_params["deadline"] = pytezos.now() + 100
        opg = dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        with open('../../remove_liquidity_gas.txt', 'a') as f:
            f.write(
                f'new remove_liquidity with no baker_rewards call : {consumed_gas} gas; \n')

    def test_remove_liquidity_gas_consumption_xtz(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).with_amount(
            amount_a).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"xtz": None}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        remove_amount = 10 ** 6
        remove_liquidity_params = Dex.remove_liquidity_params
        remove_liquidity_params["rem_to"] = ALICE_PK
        remove_liquidity_params["lqt_burned"] = remove_amount
        remove_liquidity_params["min_token_a_withdrawn"] = remove_amount * \
            amount_a // lqt_total
        remove_liquidity_params["min_token_b_withdrawn"] = remove_amount * \
            amount_b // lqt_total
        remove_liquidity_params["deadline"] = pytezos.now() + 100
        opg = dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        with open('../../remove_liquidity_gas.txt', 'a') as f:
            f.write(
                f'new remove_liquidity with baker_rewards call : {consumed_gas} gas; \n')

    def test11_it_fails_when_token_a_withdrawn_is_lesser_than_min_tokens_withdrawn(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        remove_amount = lqt_total // 100
        remove_liquidity_params = Dex.remove_liquidity_params
        remove_liquidity_params["rem_to"] = ALICE_PK
        remove_liquidity_params["lqt_burned"] = remove_amount
        remove_liquidity_params["min_token_b_withdrawn"] = remove_amount * \
            amount_b // lqt_total
        remove_liquidity_params["deadline"] = pytezos.now() + 100
        with self.assertRaises(MichelsonError) as err:
            remove_liquidity_params["min_token_a_withdrawn"] = remove_amount * \
                amount_a // lqt_total + 1
            dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "211"})

    def test12_it_fails_when_token_b_withdrawn_is_lesser_than_min_tokens_withdrawn(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        remove_amount = lqt_total // 100
        remove_liquidity_params = Dex.remove_liquidity_params
        remove_liquidity_params["rem_to"] = ALICE_PK
        remove_liquidity_params["lqt_burned"] = remove_amount
        remove_liquidity_params["min_token_a_withdrawn"] = remove_amount * \
            amount_a // lqt_total
        remove_liquidity_params["deadline"] = pytezos.now() + 100
        with self.assertRaises(MichelsonError) as err:
            remove_liquidity_params["min_token_b_withdrawn"] = remove_amount * \
                amount_b // lqt_total + 1
            dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "211"})

    def test13_it_fails_when_burn_amount_is_greater_than_the_total_lqt(self):
        factory, _, _ = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
        factory.launchExchange(launch_exchange_params).send(**send_conf)
        dex_address = factory.storage["pairs"][(
            {"fa12": token_a.address}, {"fa12": token_b.address})]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        lqt_total = dex.storage["lqt_total"]()
        remove_amount = lqt_total + 1
        remove_liquidity_params = Dex.remove_liquidity_params
        remove_liquidity_params["rem_to"] = ALICE_PK
        remove_liquidity_params["min_token_a_withdrawn"] = remove_amount * \
            amount_a // lqt_total
        remove_liquidity_params["min_token_b_withdrawn"] = remove_amount * \
            amount_b // lqt_total
        remove_liquidity_params["deadline"] = pytezos.now() + 100
        with self.assertRaises(MichelsonError) as err:
            remove_liquidity_params["lqt_burned"] = remove_amount
            dex.removeLiquidity(remove_liquidity_params).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "212"})

    def test20_it_swaps_successfully_fa12_xtz(self):
        factory, _, sink = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_a = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"xtz": None}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"mutez": None}
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

        consumed_gas = OperationResult.consumed_gas(resp.opg_result)
        fee = resp.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap fa1.2 to xtz : {consumed_gas} gas; {fee} mutez fee; \n')

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
        # breakpoint()
        self.assertEqual(token_a.storage["tokens"][dex_address](
        ), amount_a + tokens_sold - (burn_amount + reserve_amount))

    def test21_it_swaps_successfully_xtz_fa12(self):
        factory, _, sink = Env().deploy_full_app()
        fa12_init_storage = FA12Storage()
        token_b = Env().deploy_fa12(fa12_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_b.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        launch_exchange_params["token_amount_b"] = {"amount": amount_a}
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

        resp = dex.swap(swap_params).with_amount(tokens_sold).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(resp.opg_result)
        fee = resp.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap xtz to fa1.2 : {consumed_gas} gas; {fee} mutez fee; \n')

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]
        # breakpoint()
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

    def test22_it_swaps_successfully_fa2_xtz(self):
        factory, _, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_a = Env().deploy_fa2(fa2_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa2": (token_a.address, 0)}
        launch_exchange_params["token_type_b"] = {"xtz": None}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "amount": amount_a,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_a.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"mutez": None}
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

        consumed_gas = OperationResult.consumed_gas(resp.opg_result)
        fee = resp.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap fa2 to xtz : {consumed_gas} gas; {fee} mutez fee; \n')

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
        # breakpoint()
        self.assertEqual(token_a.storage["ledger"][(dex_address, 0)](
        ), amount_a + tokens_sold - (burn_amount + reserve_amount))

    def test23_it_swaps_successfully_xtz_fa2(self):
        factory, _, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_b = Env().deploy_fa2(fa2_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {"fa2": (token_b.address, 0)}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_b.mint({"address": ALICE_PK, "amount": amount_b,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_b.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

        resp = dex.swap(swap_params).with_amount(tokens_sold).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(resp.opg_result)
        fee = resp.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap xtz to fa2 : {consumed_gas} gas; {fee} mutez fee; \n')

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

    def test24_it_swaps_successfully_fa12_fa2(self):
        factory, _, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_a = Env().deploy_fa12(FA12Storage())
        token_b = Env().deploy_fa2(fa2_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa2": (token_b.address, 0)}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "amount": amount_b,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_b.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

        opg = dex.swap(swap_params).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap fa1.2 to fa2 : {consumed_gas} gas; {fee} mutez fee; \n')

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

    def test25_it_swaps_successfully_fa2_fa12(self):
        factory, _, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa2(FA2Storage())
        token_b = Env().deploy_fa12(FA12Storage())
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa2": (token_a.address, 0)}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "amount": amount_a,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_a.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

        opg = dex.swap(swap_params).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap fa2 to fa1.2 : {consumed_gas} gas; {fee} mutez fee; \n')

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

    def test26_it_swaps_successfully_fa12_fa12(self):
        factory, _, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa12(FA12Storage())
        token_b = Env().deploy_fa12(FA12Storage())
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

        opg = dex.swap(swap_params).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap fa1.2 to fa1.2 : {consumed_gas} gas; {fee} mutez fee; \n')

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

    def test27_it_swaps_successfully_fa2_fa2(self):
        factory, _, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa2(FA2Storage())
        token_b = Env().deploy_fa2(FA2Storage())
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa2": (token_a.address, 0)}
        launch_exchange_params["token_type_b"] = {"fa2": (token_b.address, 0)}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "amount": amount_a,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_a.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "amount": amount_b,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_b.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

        opg = dex.swap(swap_params).send(**send_conf)

        consumed_gas = OperationResult.consumed_gas(opg.opg_result)
        fee = opg.opg_result["contents"][0]["fee"]

        with open('../../swap_gas.txt', 'a') as f:
            f.write(
                f'new swap fa2 to fa2 : {consumed_gas} gas; {fee} mutez fee; \n')

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

    def test28_it_swaps_successfully_fa12_fa12_flat(self):
        factory, _, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa12(FA12Storage())
        token_b = Env().deploy_fa12(FA12Storage())
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["curve"] = {"flat": None}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

    def skip_test29_it_compares_curve_swaps_fa12_fa12_flat(self):
        factory, _, sink = Env().deploy_full_app()

        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
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

            launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
            launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
            launch_exchange_params["token_amount_a"] = {"amount": amount_a}
            launch_exchange_params["token_amount_b"] = {"amount": amount_b}
            launch_exchange_params["curve"] = {"product": None}
            factory.launchExchange(launch_exchange_params).send(**send_conf)

            launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
            launch_exchange_params["token_type_b"] = {"fa12": token_c.address}
            launch_exchange_params["token_amount_a"] = {"amount": amount_a}
            launch_exchange_params["token_amount_b"] = {"amount": amount_b}
            launch_exchange_params["curve"] = {"flat": None}
            factory.launchExchange(launch_exchange_params).send(**send_conf)

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
            f = (abs((amount_a + amount_b) ** 8) - ((amount_a - amount_b) ** 8))
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

    def test30_it_fails_when_token_is_xtz_and_no_amount_was_sent(self):
        factory, _, sink = Env().deploy_full_app()
        fa2_init_storage = FA2Storage()
        token_b = Env().deploy_fa2(fa2_init_storage)
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"xtz": None}
        launch_exchange_params["token_type_b"] = {"fa2": (token_b.address, 0)}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_b.mint({"address": ALICE_PK, "amount": amount_b,
                      "metadata": {}, "token_id": 0}).send(**send_conf)
        token_b.update_operators([{"add_operator": {
            "owner": ALICE_PK, "operator": factory.address, "token_id": 0}}]).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"mutez": None}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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

    def test31_it_fails_when_token_is_not_xtz_and_amount_is_sent(self):
        factory, _, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa12(FA12Storage())
        token_b = Env().deploy_fa12(FA12Storage())
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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
            dex.swap(swap_params).with_amount(tokens_sold).send(**send_conf)
        self.assertEqual(err.exception.args[0]["with"], {"int": "231"})

    def test32_it_fails_when_tokens_bought_below_min_tokens_bought(self):
        factory, _, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa12(FA12Storage())
        token_b = Env().deploy_fa12(FA12Storage())
        liquidity_token = Env().deploy_liquidity_token(LqtStorage())
        launch_exchange_params = Factory.launch_exchange_params
        launch_exchange_params["token_type_a"] = {"fa12": token_a.address}
        launch_exchange_params["token_type_b"] = {"fa12": token_b.address}
        launch_exchange_params["lp_address"] = liquidity_token.address
        amount_a = 10 ** 6
        amount_b = 10 ** 6
        token_a.mint({"address": ALICE_PK, "value": amount_a}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                        "value": amount_a}).send(**send_conf)
        token_b.mint({"address": ALICE_PK, "value": amount_b}
                     ).send(**send_conf)
        token_b.approve({"spender": factory.address,
                        "value": amount_b}).send(**send_conf)
        launch_exchange_params["token_amount_a"] = {"amount": amount_a}
        launch_exchange_params["token_amount_b"] = {"amount": amount_b}
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
