#if !COMMON_MISC
#define COMMON_MISC

#include "common_interface.mligo"
#include "common_errors.mligo"
[@inline]
let check_tezos_amount_is_zero () =
  if Tezos.amount > 0mutez
  then (failwith error_AMOUNT_MUST_BE_ZERO : unit)
  else ()


[@inline]
let check_id_is_equal (id_a : fa_token) (id_b : fa_token) =
  match (id_a, id_b) with
  | (FA12, FA12) -> true
  | (FA2 i, FA2 j) -> i = j
  | _ -> false


[@inline]
let check_tokens_are_equal ((addr_a, id_a) : (address * fa_token)) ((addr_b, id_b) : (address * fa_token)) =
  (addr_a = addr_b) && (check_id_is_equal id_a id_b)


[@inline]
let check_sender (addr : address) =
  if Tezos.sender <> addr
  then (failwith error_CALL_NOT_FROM_AN_IMPLICIT_ACCOUNT : unit)
  else ()


[@inline]
let sqrt (y : nat) =
  if y > 3n
  then
    let z = y in
    let x = (y / 2n) + 1n in
    let rec iter : (nat * nat * nat) -> nat =
      fun ((x : nat), (y : nat), (z : nat)) ->
        if x < z then iter ((((y / x) + x) / 2n), y, x) else z in
    iter (x, y, z)
  else if y <> 0n then 1n else 0n


[@inline]
let get_contract_FA2_transfer (token_address : address) : fa2_transfer list contract =
  match (Tezos.get_entrypoint_opt "%transfer" token_address : fa2_transfer list
             contract option)
  with
  | None ->
    (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT_FA2 : 
       fa2_transfer list contract)
  | Some contract -> contract


[@inline]
let get_contract_FA12_transfer (token_address : address) : fa12_transfer contract =
  match (Tezos.get_entrypoint_opt "%transfer" token_address : fa12_transfer
             contract option)
  with
  | None ->
    (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT_FA12 : 
       fa12_transfer contract)
  | Some contract -> contract


[@inline]
let make_fa_transfer (opt_id : fa_token) (token_address : address) (from_addr : address) (to_addr : address) (token_amount : nat) : operation option =
  if token_amount = 0n
  then None
  else
    (match opt_id with
     | FA12 ->
       let transfer_param : fa12_transfer =
         { from = from_addr; to = to_addr; value = token_amount } in
Some
  (Tezos.transaction transfer_param 0mutez
     (get_contract_FA12_transfer token_address))
| FA2 tokenId ->
Some
  (Tezos.transaction
     [{
       from_ = from_addr;
       txs =
         [{ to_ = to_addr; token_id = tokenId; amount = token_amount
          }]
     }] 0mutez (get_contract_FA2_transfer token_address)))

#endif