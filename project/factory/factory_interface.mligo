#include "../common/interface.mligo"

type storage = 
[@layout:comb]
{
    pairs : ((token_type * token_type), address) big_map;
    pools : (nat, address) big_map;
    default_smak_token_type : token_type;
    default_reserve : address;
    default_sink : address option;
    default_lp_metadata : (string, bytes) big_map ;
    default_lp_allowances: (allowance_key, nat) big_map ;
    default_lp_token_metadata: (nat, token_metadata_entry) big_map ;
    default_baker : key_hash;
    default_reward_rate : nat;
    default_claim_limit : nat;
    default_user_rewards: (address, user_reward_info) big_map; 
    counter : nat;
    multisig : address;
}

type return = operation list * storage

type metadata =
[@layout:comb]
{
  name : string;
  version : string;
  homepage : string;
  authors : string list;
}

type token_metadata =
[@layout:comb]
{
  uri : string;
  symbol : string;
  decimals : string;
  shouldPreferSymbol : string;
  thumbnailUri : string;
}

type launch_exchange_params =
[@layout:comb]
{
    token_type_a : token_type;
    token_type_b : token_type;
    token_amount_a : token_amount;
    token_amount_b : token_amount;
    curve : curve_type;
    metadata : metadata;
    token_metadata : token_metadata;
}

type remove_exchange_param =
[@layout:comb]
{
  index : nat;
  token_a : token_type;
  token_b : token_type;
}

type set_lqt_address_params =
[@layout:comb]
{
  dex_address : address;
  lqt_address : address;
}

type set_rewards_address_param =
[@layout:comb]
{
  dex_address : address;
  rewards_address : address;
}

type set_baker_param =
[@layout:comb]
{
  baker : key_hash option;
  dex_address : address;
  freeze_baker : bool;
}

type update_baker_param =
[@layout:comb]
{
  baker : key_hash;
  first_pool : nat;
  number_of_pools : nat;
}

type update_sink_address_param =
[@layout:comb]
{
  number_of_pools : nat;
  first_pool : nat;
  new_sink_address : address;
}

type parameter =
| LaunchExchange of launch_exchange_params
| SetLqtAddress of set_lqt_address_params
| LaunchSink
| SetBaker of set_baker_param
| SetSinkClaimLimit of nat
| UpdateSinkAddress of update_sink_address_param
| RemoveExchange of remove_exchange_param
| UpdateBaker of update_baker_param
| UpdateMultisig of address