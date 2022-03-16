#include "../gen_common/interface.mligo"

//type token_type =
//| Xtz
//| Fa12 of address
//| Fa2 of (address * token_id)

//type token_address =
//| Tez
//| Token of address

//type fa_token =
//| FA2 of token_id 
//| FA12 

//type token_amount =
//| Mutez
//| Amount of nat

//type curve_type =
//| Flat
//| Product

type tokens = (address, nat) big_map

//type investment_direction = Add | Remove

//type investment_delta = {
  //token_invest_a : nat;
  //token_invest_b : nat;
  //direction : investment_direction;
//}

type allowance_key = [@layout:comb]  {
  owner: address ;
  spender: address }

type token_metadata_entry = [@layout:comb]  {
  token_id: nat ;
  token_info: (string, bytes) map }

type storage = 
[@layout:comb]
{
    pairs : ((token_type * token_type), address) big_map;
    pools : (nat, address) big_map;
    default_token_smak : address;
    default_smak_token_type : token_type;
    default_reserve : address option;
    default_lp_metadata : (string, bytes) big_map ;
    default_lp_allowances: (allowance_key, nat) big_map ;
    default_lp_token_metadata: (nat, token_metadata_entry) big_map ;
    counter : nat;
}

type return = operation list * storage

//type dex_storage =
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
//    user_investments : (address, investment_delta) big_map;
//    lqt_address : address option;
//    last_k : nat;
//    curve : curve_type;
//    manager : address;
//    freeze_baker : bool;
//}

type lp_token_storage = 
[@layout:comb]
{
  tokens: tokens ;
  allowances: (allowance_key, nat) big_map ;
  admin: address ;
  total_supply: nat ;
  metadata: (string, bytes) big_map ;
  token_metadata: (nat, token_metadata_entry) big_map 
}

type sink_storage = 
[@layout:comb]
{
    token_smak : address;
    fa_token_smak : token_type;
    factory_address : address;
}

type launch_exchange_params =
[@layout:comb]
{
    token_type_a : token_type;
    token_type_b : token_type;
    token_amount_a : token_amount;
    token_amount_b : token_amount;
    curve : curve_type;
}

type set_lqt_address_params =
[@layout:comb]
{
  dex_address : address;
  lqt_address : address;
}

type parameter =
| LaunchExchange of launch_exchange_params
| SetLqtAddress of set_lqt_address_params
| LaunchSink