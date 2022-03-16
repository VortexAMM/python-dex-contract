#if !SINK
#define SINK

[@inline]
let error_DEX_MUST_HAVE_SWAP_ENTRYPOINT  =
  300n


[@inline]
let error_TOKEN_TO_SWAP_AND_BURN_IS_ZERO  =
  301n


[@inline]
let error_TIME_IS_PASSED  =
  302n


[@inline]
let error_NO_POOL_WITH_SMAK_PAIR_IN_FACTORY  =
  303n


[@inline]
let error_FA2_CONTRACT_MUST_HAVE_UPDATE_OPERATORS_ENTRYPOINT  =
  304


[@inline]
let error_FA12_CONTRACT_MUST_HAVE_APPROVE_ENTRYPOINT  =
  305

[@inline]
let error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT  =
  306

[@inline]
let error_FA2_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT  =
  307

[@inline]
let error_NO_UNIT_CONTRACT  =
  308

[@inline]
let error_NO_AMOUNT_TO_BE_SENT  =
  309

#include "../../mixed_dex/gen_common/interface.mligo"
#include "../../mixed_dex/gen_common/functions.mligo"
#include "../../mixed_dex/gen_factory/factory_interface.mligo"
type approve_param = (address * nat)

type token_type =
| Fa12 of address
| Fa2 of (address * nat)
| Xtz

type operator_param = [@layout:comb]  {
  owner: address ;
  operator: address ;
  token_id: nat }

type operator_update = [@layout:comb] 
  | Add_operator of operator_param 
  | Remove_operator of operator_param 

type burn_param = [@layout:comb]  {
    token_to_burn_address: address ;
    token_to_burn_id: token_type ;
    to_burn: nat ;
    min_to_burn: nat ;
    swap_direction: bool ;
    deadline: timestamp }

type swap_param =
[@layout:comb]
{
    t2t_to : address;
    tokens_sold : nat;
    min_tokens_bought : nat;
    a_to_b : bool;
    deadline : timestamp;
}

type get_address_param =
{
         a_addr : address;
         a_id : token_type;
         b_addr : address;
         b_id : token_type;
         direction : bool;
       }

type return = (operation list * sink_storage)

[@inline]
let null_implicit_account  : address =
  ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address)


[@inline]
let external_swap (dex_address : address) (t : swap_param) =
  let dex : swap_param contract =
    match (Tezos.get_entrypoint_opt "%swap" dex_address : swap_param
               contract option)
    with
    | None ->
      (failwith error_DEX_MUST_HAVE_SWAP_ENTRYPOINT : swap_param contract)
    | Some contract -> contract in
  Tezos.transaction t 0mutez dex


[@inline]
let check_burn_param (burn_param : burn_param) : unit =
  if burn_param.to_burn = 0n
  then (failwith error_TOKEN_TO_SWAP_AND_BURN_IS_ZERO : unit)
  else
  if Tezos.now > burn_param.deadline
  then (failwith error_TIME_IS_PASSED : unit)
  else ()

[@inline]
let check_tezos_amount_is_zero () : unit =
  if Tezos.amount <> 0mutez then
    failwith error_NO_AMOUNT_TO_BE_SENT
  else ()


[@inline]
let external_update_operators_fa2 (fa2_addr : address) (operator_updates : operator_update list) : operation =
  let fa2 : operator_update list contract =
    match (Tezos.get_entrypoint_opt "%update_operators" fa2_addr : operator_update
               list
               contract
               option)
    with
    | None ->
      (failwith error_FA2_CONTRACT_MUST_HAVE_UPDATE_OPERATORS_ENTRYPOINT : 
         operator_update list contract)
    | Some contract -> contract in
  Tezos.transaction operator_updates 0mutez fa2


[@inline]
let external_approve_fa12 (fa12_addr : address) (to_approve : address) (amt : nat) : operation =
  let fa12 : approve_param contract =
    match (Tezos.get_entrypoint_opt "%approve" fa12_addr : approve_param
               contract option)
    with
    | None ->
      (failwith error_FA12_CONTRACT_MUST_HAVE_APPROVE_ENTRYPOINT : approve_param
           contract)
    | Some contract -> contract in
  Tezos.transaction (to_approve, amt) 0mutez fa12

let external_approve (token_id : token_type) (token_addr : address) (dex_to_approve : address) (amt : nat) : operation option =
  match token_id with
  | Fa2 (_, tokenId) ->
    let approve =
      [Add_operator
         {
           owner = Tezos.self_address;
           operator = dex_to_approve;
           token_id = tokenId
         }] in
    Some (external_update_operators_fa2 token_addr (approve : operator_update list) : operation)
  | Fa12 _ -> Some (external_approve_fa12 token_addr dex_to_approve amt : operation)
  | Xtz -> None

let burn (burn_param : burn_param) (storage : sink_storage) : return =
  let () = check_tezos_amount_is_zero () in
  let () = check_burn_param burn_param in
  let dex_address : address option =
    (Tezos.call_view "get_dex_address"
       ({
         a_addr = burn_param.token_to_burn_address;
         a_id = burn_param.token_to_burn_id;
         b_addr = storage.token_smak;
         b_id = storage.fa_token_smak;
         direction = burn_param.swap_direction
       } : get_address_param) storage.factory_address : address option) in
  match (dex_address : address option) with
  | None -> (failwith error_NO_POOL_WITH_SMAK_PAIR_IN_FACTORY : return)
  | Some dex_addr ->
    let ops = ([] : operation list) in
    let op_approve =
      external_approve burn_param.token_to_burn_id
        burn_param.token_to_burn_address dex_addr burn_param.to_burn in
    let ops = match op_approve with
    | None -> ops
    | Some op -> [op] in
    let op_swap : operation =
      external_swap dex_addr
        {
  t2t_to = null_implicit_account;
  tokens_sold = burn_param.to_burn;
  min_tokens_bought = burn_param.min_to_burn;
  a_to_b = burn_param.swap_direction;
  deadline = (burn_param.deadline : timestamp)
} in
let ops = op_swap :: ops in
ops, storage

type parameter =
| Burn of burn_param

let main (action, store : parameter * sink_storage) : return =
match action with
| Burn p -> burn p store

#endif