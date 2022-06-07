import sys
from pytezos import pytezos
from env import Env, ALICE_KEY, ALICE_PK, FA12Storage, send_conf, metadata, token_metadata

network = sys.argv[1]


if network == "sandbox":
    SHELL = "http://localhost:8732"
    DEFAULT_BAKER = ALICE_PK
elif network == "testnet":
    SHELL = "https://rpc.ithaca.tzstats.com"
    DEFAULT_BAKER = "tz1RuHDSj9P7mNNhfKxsyLGRDahTX5QD1DdP"
    ALICE_PK = "tz1Xr8Y9Yh9qMwYv8xpwjqBXi4aHR1ubQ7BU"
    ALICE_KEY = "edsk4beFJBLc8D3dsDVkYkCoDcQgsGffu7612HnMLgx6hWTS6mQCFz"
elif network == "mainnet":
    SHELL = "https://rpc.tzstats.com"
    DEFAULT_BAKER = input("Please input the factory's default baker: ")
    ALICE_PK = input("Please input tz... address: ")
    ALICE_KEY = input("Please input secret key for deployment: ")
else:
    print("No valid network was chosen")
    exit()


using_params = dict(shell=SHELL, key=ALICE_KEY)
pytezos = pytezos.using(**using_params)

print("deploy full app")
factory, smak_token, sink, multisig = Env(
    using_params).deploy_full_app(DEFAULT_BAKER, ALICE_PK)
if network != "mainnet":
    print("deploy token a of pair 1")
    pair_1_token_a = Env(using_params).deploy_fa12(FA12Storage(admin=ALICE_PK))
    print("mint token a of pair 1")
    pair_1_token_a.mint(
        {"address": ALICE_PK, "value": 10 ** 6 + 10 ** 12}).send(**send_conf)
    print("approve token a of pair 1")
    pair_1_token_a.approve({"spender": factory.address,
                            "value": 10 ** 6}).send(**send_conf)
    print("deploy token b of pair 1")
    pair_1_token_b = Env(using_params).deploy_fa12(FA12Storage(admin=ALICE_PK))
    print("mint token b of pair 1")
    pair_1_token_b.mint(
        {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
    print("approve token b of pair 1")
    pair_1_token_b.approve({"spender": factory.address,
                            "value": 10 ** 6}).send(**send_conf)
    print("deploy token a of pair 2")
    pair_2_token_a = Env(using_params).deploy_fa12(FA12Storage(admin=ALICE_PK))
    print("mint token a of pair 2")
    pair_2_token_a.mint(
        {"address": ALICE_PK, "value": 10 ** 6}).send(**send_conf)
    print("approve token a of pair 2")
    pair_2_token_a.approve({"spender": factory.address,
                            "value": 10 ** 6}).send(**send_conf)
    pair_1_launch_exchange_params = {
        "token_type_a": {"fa12": pair_1_token_a.address},
        "token_type_b": {"fa12": pair_1_token_b.address},
        "token_amount_a": {"amount": 10 ** 6},
        "token_amount_b": {"amount": 10 ** 6},
        "curve": {"product": None},
        "metadata": metadata,
        "token_metadata": token_metadata,
    }

    print("launch pair 1")
    factory.launchExchange(pair_1_launch_exchange_params).send(**send_conf)

    pair_2_launch_exchange_params = {
        "token_type_a": {"fa12": pair_2_token_a.address},
        "token_type_b": {"xtz": None},
        "token_amount_a": {"amount": 10 ** 6},
        "token_amount_b": {"mutez": 10 ** 6},
        "curve": {"product": None},
        "metadata": metadata,
        "token_metadata": token_metadata,
    }

    print("launch pair 2")
    factory.launchExchange(pair_2_launch_exchange_params).with_amount(
        10 ** 6).send(**send_conf)

    dex_1_addr = factory.storage["pairs"][({"fa12": pair_1_token_a.address}, {
                                           "fa12": pair_1_token_b.address})]()
    dex_2_addr = factory.storage["pairs"][(
        {"fa12": pair_2_token_a.address}, {"xtz": None})]()

print(f"factory address: {factory.address}")
print(f"multisig address: {multisig.address}")
print(f"sink address: {sink.address}")
if network != "mainnet":
    print(f"dex 1 address: {dex_1_addr}")
    print(f"dex 2 address: {dex_2_addr}")
