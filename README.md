# Dcentralized Exchange Contracts

This is a description of a system composing a Decentralized Exchange (DEX) network.

## User Instructions:

### setup:

run the command `docker-compose up -d`

from the folder `project` run the command `./compile.sh` to compile all contracts.

### Deploy contracts:

From the folder `project/tests` run `python3 deploy.py`  
*if deployment is to the testnet, make sure the `SHELL = "http://localhost:20000"` line is commented, and the line below is uncommented*

The `deploy.py` file is set to deploy a factory with no exchanges on it.
To deploy a factory with an assortment of exchanges on it, uncomment the last line of `deploy.py`, and comment the line above it.
The factory's address and its sink contract address will be output at the `project/real_contracts.txt` file.

Individual exchanges can be launched by calling `factory.launchExchange(params).send(**send_conf)`
With `param` as described in the "launch exchange" section.


### Testing The Contracts:

All contract tests are in the folder `project/tests`.
To run a test run `python3 -m unittest test_file_name.py`.
For example: to run the factory tests, run `python3 -m unittest test_factory.py`.
Make sure that you run `docker-compose up -d` before running the tests.

## System Architecture

The system is comprised of the following smart-contracts, which interact with each other.

- **Factory:**  
A smart contract responsible for deploying key contracts, linking them to one another, setting up their initial storages and storing some important data regarding them.

- **Dex:**
The exchange contract, which handles the exchanges between a pair of tokens `a` and `b`, the exchange rates between the two, the liquidity of the tokens and fee distribution.

- **Sink:**
A contract that collects "buyback fees" from all the different exchanges, swaps the fees to the *SMAK* token and burns the collected *SMAK* tokens.

- **Liquidity Token:**
An **FA1.2** standard token contract, handling liquidity shares of all liquidity providers for a given *DEX* contract.

- **Sink Reward:**
A contract that rewards external user when trigering the *swap and burn* mechanism of the *Swap* contract.

- **baker rewards:**
A contract handing out of the baker rewards to liquidity providers.




### launch_exchange
This entry-point is used to launch the dex  contract and initialize its storage.

**Input parameters:**  
- `token_type_a` : token input;
- `token_type_b` : token output;
- `token_amount_a` : token input amount;
- `token_amount_b` : token output amount;
- `curve` : type of dex(constant product or flat curve);
- `lp_address` : lp token address;

```mermaid 
flowchart TD
A{launch_exchange}
B((dex 1))
C((LP token 1))
D((dex 2))
E((LP token-2))
F((dex 3))
G((LP token))
H((dex 4))
I((LP token))
J((token a))
K((token b))
L((token a))
M((token b))
N((token a))
O((token b))
P((token a))
Q((token b))

subgraph Factory-contract
A
end
subgraph exchange-3
F
G
N
O
end
subgraph exchange-2
D
E
L
M
end
subgraph exchange-1
B
C
J
K
end
subgraph exchange-4
H
I
P
Q
end
B-.-C
B-.-J
B-.-K
D-.-E
D-.-L
D-.-M
F-.-G
F-.-N
F-.-O
H-.-I
H-.-P
H-.-Q
Factory-contract-.-exchange-1
Factory-contract-.-exchange-2
Factory-contract-.-exchange-3
A--->|dex_storage, lp_storage, am|exchange-4
```
### Set Liquidity Address:

```mermaid
flowchart TD
A{setLqtAddress}
B{setLqtAddress}
C((LP token))
D((token a))
E((token b))
subgraph factory contract
A
end
subgraph exchange
subgraph dex-contract
B
end
C
D
E
end
A--->|callback|A
A--->|lqt_address|B
dex-contract-.-C
dex-contract-.-D
dex-contract-.-E
```
### launch_sink
This entry-point is used to launch the sink contract.

### set_sink_claim_limit
This entry-point is used to update the maximum number of tokens allowed for the smak claim  (against the smak swap and burn).

**Input parameters:**  
- `param` : maximum number of tokens to be swaped to smak per user claim transaction.
---

## Dex

### add_liquidity

This entry-point is used to add liquidity to the pool.

**Input parameters:** 

- `owner` : address of the liquidity provider;
- `amount_token_a` : token input amount;
- `min_lqt_minted` : minmum lp amount accepted ;
- `max_tokens_deposited` : maximum token output amount accepted  ;
- `deadline` : the deadline of the transaction;

```mermaid
flowchart TD
A{addLiquidity}
B1[dex]
B2[provider]
C1[dex]
C2[provider]
D[provider]
E[(lqt total)]
F[(pool a)]
G[(pool b)]
H{mintOrBurn}
I[provider]
subgraph dex-contract
A
subgraph storage
E
F
G
end
end
subgraph token-a-contract
subgraph token-a-ledger
B1
B2
end
end
subgraph token-b-contract
subgraph token-b-ledger
C1
C2
end
end
subgraph LP-contract
H-.->|mint|I
subgraph LP-ledger
I
end
end
D-->|tokn-a-amount|A
A--->|tokens A deposited|token-a-ledger
A--->|tokens A deposited|token-b-ledger
A-.->|lqt minted|E
A-.->|tokens A deposited|F
A-.->|tokens B deposited|G
A--->|lqt minted|H
B2-.->|token-a-amount|B1
C2-.->|token-b-amount|C1
```

### remove_liquidity 
This entry-point is used to remove liquidity from the pool.

**Input parameters:** 

- `rem_to` : destination address ;
- `lqt_burned` : lp token amount;
- `min_token_a_withdrawn` : minmum token input amount accepted ;
- `min_token_b_withdrawn` : minmum token output amount accepted  ;
- `deadline` : the deadline of the transaction;

```mermaid
flowchart TD
A{removeLiquidity}
B1(dex)
B2(provider)
C1(dex)
C2(provider)
D(provider)
E[(lqt total)]
F[(token a pool)]
G[(token b pool)]
H{mintOrBurn}
I(provider)
subgraph dex-contract
A
subgraph storage
E
F
G
end
end
subgraph token-a-contract
subgraph token-a-ledger
B1
B2
end
end
subgraph token-b-contract
subgraph token-b-ledger
C1
C2
end
end
subgraph LP-contract
H-.->|burn|I
subgraph LP-ledger
I
end
end
D-->|lqt burned|A
A--->|tokens a withdrawn|token-a-ledger
A--->|tokens b withdrawn|token-b-ledger
A-.->|lqt burned|E
A-.->|tokens a withdrawn|F
A-.->|tokens b withdrawn|G
A--->|lqt burned|H
B1-.->|tokens a withdrawn|B2
C1-.->|tokens b withdrawn|C2
```

### swap

This entry-point is used to swap token a to token b.

**Input parameters:** 

- `t2t_to`: destination address ;
- `tokens_sold`: token input amount;
- `min_tokens_bought` : minmum token output amount accepted ;
- `a_to_b` : the direction of the swap ( if true from token a to token b , otherwise from token b to token a);
- `deadline` : the deadline of the transaction;

- This graph represents the general case, when both token_a and token_b are `fa1.2` or `fa2` fungible tokens. For the case when one of the tokens is `XTZ`, the model is the same, except that no `transfer` call is being made, but the amount is either deposited in the `dex` contract or transferred out of it.  
- In the graph, `token a` reffers to the sold token, and `token b` to the bought token. This is not always the case - the swap can be reversed to `token a` being the bought token and `token b` being the sold token. 

```mermaid
flowchart TD
A(alice)
B{swap}
C[(token a pool)]
D[(token b pool)]
E1(alice)
E2(dex)
F{transfer}
G{deposit}
H{transfer}
H1(alice)
H2(dex)
H3(sink)
subgraph dex-contract
B
subgraph dex-storage
C
D
end
end
subgraph token b contract
F
subgraph token-b-ledger
E1
E2
end
end
subgraph token a contract
H
subgraph token-a-ledger
H1
H2
H3
end
end
subgraph sink
G
end
A-->|tokens sold|B
B-->|tokens sold - platform fees|C
B-->|tokens bought|D
B-->|platform fees|G
B--->|tokens bought|F
B--->|tokens sold|H
F-.->token-b-ledger
H-.->token-a-ledger
E2-.->|tokens bought|E1
H1-.->|tokens sold - platform fees|H2
H1-.->|platform fees|H3
```

### Sink Claim

```mermaid
flowchart TD
A(Alice)
B{claim}
C[get_dex_address]
D(smak-token)
E{token to smak swap}
F(sink)
G(null address)
H(beneficiary)

subgraph factory
C
subgraph pairs
D
end
end
subgraph sink
B
end
subgraph dex
E
end
subgraph smak-fa12
subgraph tokens
F
G
H
end
end
A-->B
B-.->|smak and token addresses|C-.->pairs
D-.->|dex address|B
B-->|tokens to swap|E
E-->|swaped smak|tokens
F-->|tokens to burn|G
F-->|reward|H
```


# Contract addresses:
Factory with no exchanges: KT1Dnzyn5Jx2C3Pb21G436KKjv1akRUs7e5Y
Sink: KT1KeJXrkuYJQV1Jwf1f5oWnmM4S7jFmJo3F

Factory with exchanges: KT1RQJwAQpvjTPDAQmWBAyMcLekh5LUpaKV8
Sink: KT1KJhuGpn8QvKDDB8nYvVyVvbiUZTDvBMpC
Exchange 1: KT1MJcPSBxei9v1TtQkBikcftd5omsPE48gm
Liquidity token 1: KT1NBcrbsKjmjnSGxBaqwDRr3Xo4AYg2fFVp
Exchange 2: KT1EDx1yf837ucDTF5zGRynUiJrx8UXHaTPV
Liquidity token 2: KT19UeguSJgcZSDc5ufExQ7KTkVzNrnzx7R4 