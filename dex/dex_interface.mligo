#include "../common/interface.mligo"

type a_or_b = A | B

type amounts_and_fees = 
[@layout:comb]
{
    amount_in_A : nat;
    amount_in_B : nat;
    reserve_fee_in_A : nat;
    reserve_fee_in_B : nat;
}

type newton_param =  {x : nat ; y : nat ; dx : nat ; dy : nat ; u : nat ; n : int}

type add_liquidity_param = 
[@layout:comb]
{
    owner : address;
    amount_token_a : nat;
    min_lqt_minted : nat;
    max_tokens_deposited : nat;
    deadline : timestamp;
}

type remove_liquidity_param = 
[@layout:comb]
{
    rem_to : address;
    lqt_burned : nat;
    min_token_a_withdrawn : nat;
    min_token_b_withdrawn : nat;
    deadline : timestamp;
}


type set_baker_param = dex_set_baker_param

type swap_param = dex_swap_param

type set_lqt_address_param = address

type update_reserve_param = address

type update_token_pool_internal =
  | FA12InternalA of fa12_update_token_pool_internal
  | FA2InternalA of fa2_update_token_pool_internal
  | FA12InternalB of fa12_update_token_pool_internal
  | FA2InternalB of fa2_update_token_pool_internal
  | UpdateTokenEnded 

type update_token_pool_param = unit

type storage = dex_storage

type return = operation list * storage

type parameter =
| Default
| AddLiquidity of add_liquidity_param
| RemoveLiquidity of remove_liquidity_param
| SetBaker of set_baker_param
| SetLqtAddress of set_lqt_address_param
| Swap of swap_param
| UpdateSinkAddress of address
| UpdateTokenPoolInternal of update_token_pool_internal
| UpdateTokenPool of update_token_pool_param
| ClaimReward of address