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
    counter : nat;
    default_claim_limit : nat;
    admin : address;
}

type return = operation list * storage

type launch_exchange_params =
[@layout:comb]
{
    token_type_a : token_type;
    token_type_b : token_type;
    token_amount_a : token_amount;
    token_amount_b : token_amount;
    curve : curve_type;
    lp_address : address;
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

type parameter =
| LaunchExchange of launch_exchange_params
| SetLqtAddress of set_lqt_address_params
| SetRewardsAddress of set_rewards_address_param
| LaunchSink
| SetBaker of set_baker_param
| SetSinkClaimLimit of nat