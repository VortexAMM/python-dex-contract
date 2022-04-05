from pytezos import pytezos
from tests.test_env import Env, ALICE_KEY, ALICE_PK, FA12Storage, send_conf

# Hangzhounet shell:
SHELL = "https://rpc.hangzhou.tzstats.com"

# Ithacanet shell:
# SHELL = "https://rpc.ithaca.tzstats.com"

# Mainnet shell:
# SHELL = "https://rpc.tzstats.com"

using_params = dict(shell=SHELL, key=ALICE_KEY)
pytezos = pytezos.using(**using_params)


factory, smak_token, sink = Env(using_params).deploy_full_app()
pair_1_token_a = Env(using_params).deploy_fa12(FA12Storage())
pair_1_token_a.mint(
    {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
pair_1_token_a.approve({"spender": factory.address,
                        "value": 10 ** 6}).send(**send_conf)
pair_1_token_b = Env(using_params).deploy_fa12(FA12Storage())
pair_1_token_b.mint(
    {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
pair_1_token_b.approve({"spender": factory.address,
                        "value": 10 ** 6}).send(**send_conf)
pair_2_token_a = Env(using_params).deploy_fa12(FA12Storage())
pair_2_token_a.mint(
    {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
pair_2_token_a.approve({"spender": factory.address,
                        "value": 10 ** 6}).send(**send_conf)
pair_1_launch_exchange_params = {
    "token_type_a": {"fa12": pair_1_token_a.address},
    "token_type_b": {"fa12": pair_1_token_b.address},
    "token_amount_a": {"amount": 10 ** 6},
    "token_amount_b": {"amount": 10 ** 6},
    "curve": {"product": None},
}

factory.launchExchange(pair_1_launch_exchange_params).send(**send_conf)

pair_2_launch_exchange_params = {
    "token_type_a": {"fa12": pair_2_token_a.address},
    "token_type_b": {"xtz": None},
    "token_amount_a": {"amount": 10 ** 6},
    "token_amount_b": {"mutez": 10 ** 6},
    "curve": {"product": None},
}

factory.launchExchange(pair_2_launch_exchange_params).with_amount(
    10 ** 6).send(**send_conf)

dex_1_addr = factory.storage["pairs"][({"fa12": pair_1_token_a.address}, {
                                       "fa12": pair_1_token_b.address})]()
dex_2_addr = factory.storage["pairs"][(
    {"fa12": pair_2_token_a.address}, {"xtz": None})]()

print(f"factory address: {factory.address}")
print(f"sink address: {sink.address}")
print(f"dex 1 address: {dex_1_addr}")
print(f"dex 2 address: {dex_2_addr}")
