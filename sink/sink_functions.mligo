#if !SINK_FUNCTIONS
#define SINK_FUNCTIONS
#include "../common/functions.mligo"

[@inline]
let null_implicit_account = ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address)

[@inline]
let natural_to_mutez (a: nat): tez = a * 1mutez

[@inline]
let external_swap (dex_address : address) (t : dex_swap_param) (xtz_to_send : tez) =
  let dex : dex_swap_param contract =
    match (Tezos.get_entrypoint_opt "%swap" dex_address : dex_swap_param contract option) with
    | None -> (failwith error_DEX_MUST_HAVE_SWAP_ENTRYPOINT : dex_swap_param contract)
    | Some contract -> contract in
  Tezos.transaction t xtz_to_send dex


[@inline]
let external_update_operators_fa2 (fa2_addr : address) (operator_updates : operator_update list) : operation =
  let fa2 : operator_update list contract =
    match (Tezos.get_entrypoint_opt "%update_operators" fa2_addr : operator_update list contract option) with
    | None ->
      (failwith error_FA2_CONTRACT_MUST_HAVE_UPDATE_OPERATORS_ENTRYPOINT : operator_update list contract)
    | Some contract -> contract in
  Tezos.transaction operator_updates 0mutez fa2


[@inline]
let external_approve_fa12 (fa12_addr : address) (to_approve : address) (amt : nat) : operation =
  let fa12 : approve_param contract =
    match (Tezos.get_entrypoint_opt "%approve" fa12_addr : approve_param contract option) with
    | None ->
      (failwith error_FA12_CONTRACT_MUST_HAVE_APPROVE_ENTRYPOINT : approve_param contract)
    | Some contract -> contract in
  Tezos.transaction (to_approve, amt) 0mutez fa12

let external_approve (token_type : token_type) (dex_to_approve : address) (amt : nat) : operation option =
  match token_type with
  | Fa12 token_address -> Some (external_approve_fa12 token_address dex_to_approve amt : operation)
  | _ -> None


#endif