#if !LQT_INTERFACE
#define LQT_INTERFACE

#include "../common/interface.mligo"

type transfer_param = fa12_contract_transfer


type approve_param =
  [@layout:comb]
  { spender : address;
    value : nat }

type mint_or_burn_param = mint_or_burn


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


type allowances = (allowance_key, nat) big_map


type storage = lp_token_storage


type parameter =
  | Transfer of transfer_param
  | Approve of approve_param
  | MintOrBurn of mint_or_burn_param
  | GetAllowance of get_allowance_param
  | GetBalance of get_balance_param
  | GetTotalSupply of get_total_supply_param

type return = operation list * storage

#endif