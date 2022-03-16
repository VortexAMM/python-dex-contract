#if !COMMON_INTERFACE
#define COMMON_INTERFACE

type token_id = nat

type token_type =
| Xtz
| Fa12 of address
| Fa2 of (address * token_id)

type fa_token =
| FA2 of (address * token_id) 
| FA12 of address

type token_amount =
| Mutez
| Amount of nat

type curve_type =
| Flat
| Product

type fa12_contract_transfer =
[@layout:comb]
{
    [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat; 
}

type tokens = (address, nat) big_map

type transfer_destination =
[@layout:comb]
{
  to_ : address;
  token_id : token_id;
  amount : nat;
}

type fa2_contract_transfer =
[@layout:comb]
{
  from_ : address;
  txs : transfer_destination list;
}

type balance_of_request =
[@layout:comb]
{
    owner : address;
    token_id : token_id;
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

type allowance_key =
[@layout:comb]
{
  owner: address ;
  spender: address;
}

type token_metadata_entry =
[@layout:comb]
{
  token_id: nat ;
  token_info: (string, bytes) map;
}

type get_balance_fa12 = (address * nat contract)

type fa2_update_token_pool_internal = ((address * nat) * nat) list

type fa12_update_token_pool_internal = nat

type mint_or_burn = 
[@layout:comb]
{
    quantity : int; 
    target : address
}

type baker_rewards_provider_data =
[@layout:comb]
{
    counter : nat;
    lqt_shares : nat;
    accumulated : tez;
}

type baker_rewards_history =
[@layout:comb]
{
    total_lqt : nat;
    total_fees : tez;
}

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

type baker_rewards_storage =
[@layout:comb]
{
    providers : (address, baker_rewards_provider_data) big_map;
    total_lp_tokens : nat;
    dex_address : address;
    lqt_history : (nat , baker_rewards_history) big_map;
    counter : nat;
}

type sink_storage = 
[@layout:comb]
{
    token_type_smak : token_type;
    factory_address : address;
    burn : (token_type, nat) big_map;
    reserve : (token_type, nat) big_map;
    reserve_address : address;
    token_claim_limit : nat;
    exchanges : ((token_type * token_type), address) big_map
}

type dex_storage =
[@layout:comb]
{
    self_is_updating_token_pool : bool;
    token_pool_a : nat;
    token_pool_b : nat;
    token_type_a : token_type;
    token_type_b : token_type;
    token_type_smak : token_type;
    reserve : address;
    lqt_address : address option;
    lqt_total : nat;
    curve : curve_type;
    manager : address;
    freeze_baker : bool;
    sink : address;
    baker_rewards : address option;
    reward_rate : nat;
}

type get_dex_address_param =
[@layout:comb]
{
  a_type : token_type;
  b_type : token_type;
}

type dex_swap_param =
[@layout:comb]
{
    t2t_to : address;
    tokens_sold : nat;
    min_tokens_bought : nat;
    a_to_b : bool;
    deadline : timestamp;
}

type dex_set_baker_param =
[@layout:comb]
{ 
    baker : key_hash option;
    freeze_baker : bool;
}

type sink_burn_param = 
[@layout:comb]
{
    token_to_burn_type: token_type ;
    to_burn: nat ;
    min_to_burn: nat ;
    swap_direction: bool ;
    deadline: timestamp 
}

type sink_deposit_params =
[@layout:comb]
{
  token_to_deposit : token_type;
  reference_token : token_type;
  burn_amount : nat;
  reserve_amount : nat;
  direction : bool;
}

type sink_add_exchange_param =
[@layout:comb]
{
  dex_address : address;
  token_a : token_type;
  token_b : token_type;
}

type baker_rewards_add_lqt =
[@layout:comb]
{
  lqt_minted : nat;
  owner : address;
}

type baker_rewards_remove_lqt = nat

[@inline]
let null_implicit_account = ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address)

#endif