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

type investment_direction =
| Add
| Remove

type user_investment =
[@layout:comb]
{
    token_invest_a : nat;
    token_invest_b : nat;
    direction : investment_direction;
}

type fa12_contract_transfer =
[@layout:comb]
{
    [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat; 
}

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
    lqt_total : nat;
    history : (string, nat) big_map;
    user_investments : (address, user_investment) big_map;
    lqt_address : address option;
    last_k : nat;
    curve : curve_type;
    manager : address;
    freeze_baker : bool;
}

#endif