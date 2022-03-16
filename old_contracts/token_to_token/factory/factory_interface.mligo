#if !FACTORY_TYPES
#define FACTORY_TYPES

#include "../common/common_interface.mligo"
type allowance_key = [@layout:comb]  {
  owner: address ;
  spender: address }

type tokens = (address, token) big_map

type token_metadata_entry = [@layout:comb]  {
  token_id: nat ;
  token_info: (string, bytes) map }

type lp_token_storage = [@layout:comb]  {
    tokens: tokens ;
    allowances: (allowance_key, nat) big_map ;
    admin: address ;
    total_supply: nat ;
    metadata: (string, bytes) big_map ;
    token_metadata: (nat, token_metadata_entry) big_map }

type set_lqt_address_param = [@layout:comb]  {
  dex_address: address ;
  lqt_address: address }

type launch_exchange_param =
[@layout:comb]
{
    address_a: address ;
    id_a: fa_token ;
    amount_a: nat ;
    address_b: address ;
    id_b: fa_token ;
    amount_b: nat;
    curve : curve_type;
}

type route_param_elem =
  {
    dex_addr: address ;
    token_a: (address * fa_token) ;
    token_b: (address * fa_token) ;
    swap_direction: bool }

type route_param = route_param_elem list

type param =
  | LaunchExchange of launch_exchange_param 
  | SetLqtAddress of set_lqt_address_param 
  | LaunchSink 

type storage = [@layout:comb]  {
    pools: (nat, address) big_map ;
    counter: nat ;
    pairs: (((address * fa_token) * (address * fa_token)), address) big_map ;
    default_token_smak: address ;
    default_smak_fa_token: fa_token ;
    default_reserve: address option ;
    default_lp_allowances: (allowance_key, nat) big_map ;
    default_lp_token_metadata: (nat, token_metadata_entry) big_map ;
    default_lp_metadata: (string, bytes) big_map }

type result = (operation list * storage)

#endif