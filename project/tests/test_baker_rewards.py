from unittest import TestCase
from test_env import Env, FA12Storage, ALICE_PK, send_conf, _using_params, pytezos, bob_pytezos, BOB_PK, charlie_pytezos, CHARLIE_PK
from pytezos.contract.result import OperationResult


class TestLpRewards(TestCase):
    def test_default_transaction(self):
        factory, smak_token, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa12(FA12Storage())
        token_a_type = {"fa12": token_a.address}
        token_b_type = {"xtz": None}
        token_a.mint({"address": ALICE_PK, "value": 10 ** 10}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                         "value": 10 ** 10}).send(**send_conf)
        launch_exchange_params = {
            "token_type_a": token_a_type,
            "token_type_b": token_b_type,
            "token_amount_a": {"amount": 10 ** 10},
            "token_amount_b": {"mutez": None},
            "curve": "product",
            "lp_address": ALICE_PK,
        }
        factory.launchExchange(launch_exchange_params).with_amount(
            10 ** 10).send(**send_conf)

        dex_address = factory.storage["pairs"][(token_a_type, token_b_type)]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        pytezos.transaction(destination=dex_address,
                            amount=10 ** 6).send(**send_conf)
        # breakpoint()
        baker_rewards_addr = dex.storage["baker_rewards"]()
        baker_rewards = pytezos.contract(
            baker_rewards_addr).using(**_using_params)
        self.assertEqual(baker_rewards.context.get_balance(), 10 ** 6)

    def test_deposit_to_baker_rewards_and_claim(self):
        factory, smak_token, sink = Env().deploy_full_app()
        token_a = Env().deploy_fa12(FA12Storage())
        token_a_type = {"fa12": token_a.address}
        token_b_type = {"xtz": None}
        token_a.mint({"address": ALICE_PK, "value": 10 ** 10 + 10 ** 5}
                     ).send(**send_conf)
        token_a.approve({"spender": factory.address,
                         "value": 10 ** 10}).send(**send_conf)
        launch_exchange_params = {
            "token_type_a": token_a_type,
            "token_type_b": token_b_type,
            "token_amount_a": {"amount": 10 ** 10},
            "token_amount_b": {"mutez": None},
            "curve": "flat",
            "lp_address": ALICE_PK,
        }
        factory.launchExchange(launch_exchange_params).with_amount(
            10 ** 10).send(**send_conf)

        dex_address = factory.storage["pairs"][(token_a_type, token_b_type)]()
        dex = pytezos.contract(dex_address).using(**_using_params)
        token_a.approve({"spender": dex_address,
                         "value": 10 ** 5}).send(**send_conf)
        baker_rewards_addr = dex.storage["baker_rewards"]()
        baker_rewards = pytezos.contract(
            baker_rewards_addr).using(**_using_params)
        liquidity_token_addr = dex.storage["lqt_address"]()
        liquidity_token = pytezos.contract(
            liquidity_token_addr).using(**_using_params)
        for j in range(6):
            if j % 2 == 1:
                bob_lqt = liquidity_token.storage["tokens"][BOB_PK]()
                bob_pytezos.contract(dex_address).removeLiquidity({
                    "rem_to": BOB_PK,
                    "lqt_burned": bob_lqt,
                    "min_token_a_withdrawn": 0,
                    "min_token_b_withdrawn": 0,
                    "deadline": pytezos.now() + 1000,
                }).send(**send_conf)
            if j % 4 == 1:
                charlie_lqt = liquidity_token.storage["tokens"][CHARLIE_PK]()
                charlie_pytezos.contract(dex_address).removeLiquidity({
                    "rem_to": CHARLIE_PK,
                    "lqt_burned": charlie_lqt,
                    "min_token_a_withdrawn": 0,
                    "min_token_b_withdrawn": 0,
                    "deadline": pytezos.now() + 1000,
                }).send(**send_conf)

            num_of_deposits = (j + 1) * 10
            for i in range(num_of_deposits):
                pytezos.transaction(destination=dex_address,
                                    amount=1).send(**send_conf)

            opg = baker_rewards.claimReward(ALICE_PK).send(**send_conf)
            consumed_gas = OperationResult.consumed_gas(opg.opg_result)
            internal_operations = opg.opg_result["contents"][0]["metadata"][
                "internal_operation_results"
            ]
            if j == 0:
                token_a.mint({"address": BOB_PK, "value": 10 ** 10 + 10 ** 5}
                             ).send(**send_conf)
                bob_pytezos.contract(token_a.address).approve({"spender": dex_address,
                                                               "value": 10 ** 10}).send(**send_conf)
                token_a.mint({"address": CHARLIE_PK, "value": 10 ** 10 + 10 ** 5}
                             ).send(**send_conf)
                charlie_pytezos.contract(token_a.address).approve({"spender": dex_address,
                                                                   "value": 10 ** 10}).send(**send_conf)

            if j % 2 == 0:
                add_liquidity_param = {
                    "owner": BOB_PK,
                    "amount_token_a": 10 ** 5,
                    "min_lqt_minted": 0,
                    "max_tokens_deposited": 10 ** 10,
                    "deadline": pytezos.now() + 1000,
                }
                bob_pytezos.contract(dex_address).addLiquidity(
                    add_liquidity_param).send(**send_conf)
            if j % 4 == 0:
                add_liquidity_param = {
                    "owner": CHARLIE_PK,
                    "amount_token_a": 10 ** 5,
                    "min_lqt_minted": 0,
                    "max_tokens_deposited": 10 ** 10,
                    "deadline": pytezos.now() + 1000,
                }
                charlie_pytezos.contract(dex_address).addLiquidity(
                    add_liquidity_param).send(**send_conf)
            reward = int(internal_operations[0]["amount"])
            self.assertEqual(reward, num_of_deposits)
            # counter = baker_rewards.storage["counter"]()
            # self.assertEqual(counter, num_of_deposits + 1)

            with open('../../baker_rewards_gas.txt', 'a') as f:
                f.write(
                    f'number of deposits : {num_of_deposits}; {consumed_gas} gas; \n')
