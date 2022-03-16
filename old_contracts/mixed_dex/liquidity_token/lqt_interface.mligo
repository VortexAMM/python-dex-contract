#if !LQT_INTERFACE
#define LQT_INTERFACE

type transfer_param =
  [@layout:comb]
  { [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat }

type approve_param =
  [@layout:comb]
  { spender : address;
    value : nat }

type mint_or_burn_param =
  [@layout:comb]
  { quantity : int ;
    target : address }

type allowance_key =
  [@layout:comb]
  { owner : address;
    spender : address }

type get_allowance_param =
  [@layout:comb]
  { request : allowance_key;
    callback : nat contract }

type get_balance_param =
  [@layout:comb]
  { owner : address;
    callback : nat contract }

type get_total_supply_param =
  [@layout:comb]
  { request : unit ;
    callback : nat contract }

type tokens = (address, nat) big_map
type allowances = (allowance_key, nat) big_map

type token_metadata_entry = {
  token_id: nat;
  token_info: (string, bytes) map;
}
type storage =
  [@layout:comb]
  { tokens : tokens;
    allowances : allowances;
    admin : address;
    total_supply : nat;
    metadata: (string, bytes) big_map;
    token_metadata : (nat, token_metadata_entry) big_map
  }

type parameter =
  | Transfer of transfer_param
  | Approve of approve_param
  | MintOrBurn of mint_or_burn_param
  | GetAllowance of get_allowance_param
  | GetBalance of get_balance_param
  | GetTotalSupply of get_total_supply_param

type return = operation list * storage

#endif