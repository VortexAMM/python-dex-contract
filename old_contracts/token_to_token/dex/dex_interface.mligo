#if !DEX_TYPES_T2T
#define DEX_TYPES_T2T

#include "../common/common_interface.mligo"
#include "dex_errors.mligo"
type a_or_b =
  | A 
  | B 

type token_lqt = nat

type add_liquidity = [@layout:comb]  {
    owner: address ;
    amount_token_a: token ;
    min_lqt_minted: token_lqt ;
    max_tokens_deposited: token ;
    deadline: timestamp }

type remove_liquidity = [@layout:comb]  {
    to_: address ;
    lqt_burned: token_lqt ;
    min_token_a_withdrawn: token ;
    min_token_b_withdrawn: token ;
    deadline: timestamp }

type fa2_update_token_pool_internal = ((address * nat) * nat) list

type fa12_update_token_pool_internal = nat

type update_token_pool_internal =
  | FA12InternalA of fa12_update_token_pool_internal 
  | FA2InternalA of fa2_update_token_pool_internal 
  | FA12InternalB of fa12_update_token_pool_internal 
  | FA2InternalB of fa2_update_token_pool_internal 
  | UpdateTokenEnded 

type common_entrypoint =
  | Swap of token_to_token 
  | AddLiquidity of add_liquidity 
  | RemoveLiquidity of remove_liquidity 
  | SetLqtAddress of address 
  | UpdateTokenPool 
  | UpdateTokenPoolInternal of update_token_pool_internal 

type storage = dex_storage

type result = (operation list * storage)

type fa2_transfer_destination = [@layout:comb]  {
  to_: address ;
  token_id: nat ;
  amount: nat }

type fa2_transfer = [@layout:comb]  {
  from_: address ;
  txs: fa2_transfer_destination list }

type ledger = (address, nat) big_map

type operators_storage = ((address * address), unit) big_map

type token_metadata_storage = (nat, (nat * (string, bytes) map)) big_map

type fa2_storage =
  {
    admin: address ;
    pending_admin: address option ;
    paused: bool ;
    ledger: ledger ;
    operators: operators_storage ;
    token_metadata: token_metadata_storage ;
    supply: nat ;
    metadata: (string, bytes) big_map }

type balance_of_request = [@layout:comb]  {
  owner: address ;
  token_id: nat }

type balance_of_response = [@layout:comb]  {
  request: balance_of_request ;
  balance: nat }

type balance_of_param = [@layout:comb]  {
    requests: balance_of_request list ;
    callback: balance_of_response list contract }

type get_balance_fa12 = (address * nat contract)

type mint_or_burn = [@layout:comb]  {
  quantity: int ;
  target: address }

type amounts_and_fees =
  {
    amount_in_A: nat ;
    amount_in_B: nat ;
    reserve_fee_in_A: nat ;
    reserve_fee_in_B: nat }

type newton_param =  {x : nat ; y : nat ; dx : nat ; dy : nat ; u : nat ; n : int}

#endif