#include "../gen_common/interface.mligo"

// type token_id = nat

//type token_type =
//| Xtz
//| Fa12 of address
//| Fa2 of (address * token_id)

//type fa_token =
//| FA12 of address
//| FA2 of (address * token_id)

type token = nat

type is_token =
| Tez
| Token of fa_token

//type token_amount =
//| Mutez
//| Amount of nat

//type investment_direction =
//| Add
//| Remove

//type curve_type =
//| Flat
//| Product

type a_or_b = A | B

//type user_investment =
//[@layout:comb]
//{
    //token_invest_a : nat;
    //token_invest_b : nat;
    //direction : investment_direction;
//}

type amounts_and_fees = 
[@layout:comb]
{
    amount_in_A : nat;
    amount_in_B : nat;
    reserve_fee_in_A : nat;
    reserve_fee_in_B : nat;
}

type balance_of_request =
[@layout:comb]
{
    owner : address;
    token_id : nat;
}

type balance_of_response =
[@layout:comb]
{
  request : balance_of_request;
  balance : nat;
}

type balance_of_param =
[@layout:comb]
{
    requests : balance_of_request list;
    callback : balance_of_response list contract;
}

type get_balance_fa12 = (address * nat contract)

type fa2_update_token_pool_internal = ((address * nat) * nat) list

type fa12_update_token_pool_internal = nat

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


type set_baker_param = 
[@layout:comb]
{ 
    baker : key_hash option;
    freeze_baker : bool;
}

type set_lqt_address_param = address

type swap_param =
[@layout:comb]
{
    t2t_to : address;
    tokens_sold : nat;
    min_tokens_bought : nat;
    a_to_b : bool;
    deadline : timestamp;
}

type update_reserve_param = address

type fa2_update_token_pool_internal = ((address * nat) * nat) list

type fa12_update_token_pool_internal = nat

type update_token_pool_internal =
  | FA12InternalA of fa12_update_token_pool_internal
  | FA2InternalA of fa2_update_token_pool_internal
  | FA12InternalB of fa12_update_token_pool_internal
  | FA2InternalB of fa2_update_token_pool_internal
  | UpdateTokenEnded 

type update_token_pool_param = unit

type storage = dex_storage
//type storage = 
//[@layout:comb]
//{
//    self_is_updating_token_pool : bool;
//    token_pool_a : nat;
//    token_pool_b : nat;
//    token_type_a : token_type;
//    token_type_b : token_type;
//    token_type_smak : token_type;
//    reserve : address;
//    lqt_total : nat;
//    history : (string, nat) big_map;
//    user_investments : (address, user_investment) big_map;
//    lqt_address : address option;
//    last_k : nat;
//    curve : curve_type;
//    manager : address;
//    freeze_baker : bool;
//}

type mint_or_burn = 
[@layout:comb]
{
    quantity : int; 
    target : address
}

type return = operation list * storage

type parameter =
| AddLiquidity of add_liquidity_param
| RemoveLiquidity of remove_liquidity_param
| SetBaker of set_baker_param
| SetLqtAddress of set_lqt_address_param
| Swap of swap_param
| UpadteReserve of update_reserve_param
| UpdateTokenPoolInternal of update_token_pool_internal
| UpdateTokenPool of update_token_pool_param