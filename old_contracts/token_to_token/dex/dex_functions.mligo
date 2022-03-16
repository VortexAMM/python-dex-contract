#if !DEX_MISC
#define DEX_MISC

#include "dex_interface.mligo"
#include "../common/common_functions.mligo"
[@inline]
let is_a_nat (i : int) : nat option =
  is_nat i

let operation_concat (lA : operation list) (lB : operation list) =
  List.fold_left (fun ((acc : operation list), (op : operation)) -> op :: acc)
    lA lB

let opt_operation_concat (lA : operation option) (lB : operation option) : operation list =
  match (lA, lB) with
  | (None, None) -> []
  | (Some a, None) -> [a]
  | (None, Some b) -> [b]
  | (Some a, Some b) -> [a; b]


[@inline]
let ceildiv (numerator : nat) (denominator : nat) : nat =
  match ediv numerator denominator with
  | None -> (failwith "DIV by 0" : nat)
  | Some v -> let (q, r) = v in if r = 0n then q else q + 1n


[@inline]
let token_a_transfer (storage : storage) (from : address) (to_ : address) (token_amount : nat) : operation option =
  make_fa_transfer (storage.token_id_a : fa_token)
    (storage.token_address_a : address) from to_ token_amount


[@inline]
let token_b_transfer (storage : storage) (from : address) (to_ : address) (token_amount : nat) : operation option =
  make_fa_transfer (storage.token_id_b : fa_token)
    (storage.token_address_b : address) from to_ token_amount


[@inline]
let get_contract_FA2_balance_of (token_address : address) : balance_of_param contract =
  match (Tezos.get_entrypoint_opt "%balance_of" token_address : balance_of_param
             contract
             option)
  with
  | None ->
    (failwith error_INVALID_FA2_TOKEN_CONTRACT_MISSING_BALANCE_OF : balance_of_param
         contract)
  | Some contract -> contract


[@inline]
let get_contract_FA12_get_balance (token_address : address) : get_balance_fa12 contract =
  match (Tezos.get_entrypoint_opt "%getBalance" token_address : get_balance_fa12
             contract
             option)
  with
  | None ->
    (failwith error_INVALID_FA12_TOKEN_CONTRACT_MISSING_GETBALANCE : 
       get_balance_fa12 contract)
  | Some contract -> contract


[@inline]
let check_self_is_not_updating_token_pool (storage : storage) : unit =
  if storage.self_is_updating_token_pool
  then (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : unit)
  else ()


[@inline]
let check_deadline (deadline : timestamp) : unit =
  if Tezos.now >= deadline
  then (failwith error_THE_CURRENT_TIME_MUST_BE_LESS_THAN_THE_DEADLINE : unit)
  else ()


[@inline]
let update_token_pool_internal_checks (token_address : address) (storage : storage) : unit =
  if
    (not storage.self_is_updating_token_pool) ||
    (Tezos.sender <> token_address)
  then
    (failwith
       error_THIS_ENTRYPOINT_MAY_ONLY_BE_CALLED_BY_GETBALANCE_OF_TOKENADDRESS : 
       unit)
  else (let () = check_tezos_amount_is_zero () in ())


[@inline]
let mint_or_burn (storage : storage) (target : address) (quantity : int) : operation list =
  if quantity = 0
  then ([] : operation list)
  else
    (let lqt_admin : mint_or_burn contract =
       let lqt_address =
         match storage.lqt_address with
         | None -> (failwith error_LQT_ADDRESS_IS_NOT_SET : address)
         | Some lqt_address -> lqt_address in
       match (Tezos.get_entrypoint_opt "%mintOrBurn" lqt_address : mint_or_burn
                  contract
                  option)
       with
       | None ->
         (failwith error_LQT_CONTRACT_MUST_HAVE_A_MINT_OR_BURN_ENTRYPOINT : 
            mint_or_burn contract)
       | Some contract -> contract in
     [Tezos.transaction { quantity = quantity ; target = target  } 0mutez
        lqt_admin])


[@inline]
let burn_smak (storage : storage) (from : address) (token_amount : nat) : operation option =
  make_fa_transfer (FA12 : fa_token) (storage.token_address_smak : address)
    from ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address) token_amount


[@inline]
let a_or_b_is_SMAK (storage : storage) : a_or_b option =
  if
    check_tokens_are_equal (storage.token_address_smak, storage.token_id_smak)
      (storage.token_address_a, storage.token_id_a)
  then Some A
  else
  if
    check_tokens_are_equal
      (storage.token_address_smak, storage.token_id_smak)
      (storage.token_address_b, storage.token_id_b)
  then Some B
  else None

let util (x: nat) (y: nat) : nat * nat =
    let plus = x + y in
    let minus = x - y  in
    let plus_2 = plus * plus in
    let plus_4 = plus_2 * plus_2 in
    let plus_8 = plus_4 * plus_4 in
    let plus_7 = plus_8 / plus in
    let minus_2 = minus * minus in
    let minus_4 = minus_2 * minus_2 in
    let minus_8 = minus_4 * minus_4 in
    let minus_7 = if minus = 0 then 0 else minus_8 / minus in
    (* minus_7 + plus_7 should always be positive *)
    (* since x >0 and y > 0, x + y > x - y and therefore (x + y)^7 > (x - y)^7 and (x + y^7 - (x - y)^7 > 0 *)
    (abs (plus_8 - minus_8), 8n * (abs (minus_7 + plus_7)))


let rec newton (p : newton_param) : nat =
    if p.n = 0 then
        p.dy
    else
        let new_u, new_du_dy = util (p.x + p.dx) (abs (p.y - p.dy)) in //util returns calculation of u and the derivative with respect to y
        (* new_u - p.u > 0 because dy remains an underestimate *)
        let dy = p.dy + abs ((new_u - p.u) / new_du_dy) in
        (* dy is an underestimate because we start at 0 and the utility curve is convex *)
        newton {p with dy = dy ; n = p.n - 1}


let flat (pool_a : nat) (pool_b : nat) (diff_a : nat) : nat =
    let x = pool_a in
    let y = pool_b in
    let u, _ = util x y in
    (newton {x = x; y = y ; dx = diff_a ; dy = 0n ; u = u ; n = 5})

[@inline]
let compute_fees (storage : storage) (amount_in_a : nat) (amount_in_b : nat) (feeSMAK_A : nat) (feeSMAK_B : nat) : amounts_and_fees =
  match a_or_b_is_SMAK storage with
  | Some _ ->
    {
      amount_in_A = amount_in_a;
      amount_in_B = amount_in_b;
      reserve_fee_in_A = feeSMAK_A;
      reserve_fee_in_B = feeSMAK_B
    }
  | None ->
    let k1 = storage.last_k in
    let k2 = amount_in_a * amount_in_b in
    let sqr1 = sqrt k1 in
    let sqr2 = sqrt k2 in
    (match is_a_nat (sqr2 - sqr1) with
     | None ->
       (failwith error_K2_SHOULD_BE_GREATER_THAN_K1 : amounts_and_fees)
     | Some sq2minussq1 ->
       let sm =
         (sq2minussq1 * storage.lqt_total) /
         ((ceildiv (25n * sqr2) 3n) + sqr1) in
       let arl = (sm * amount_in_a) / (storage.lqt_total + sm) in
       let brl = (sm * amount_in_b) / (storage.lqt_total + sm) in
       let new_token_pool_a =
         match is_nat (amount_in_a - arl) with
         | None -> (failwith error_A_PROTOCOL_FEE_IS_TOO_BIG : nat)
         | Some new_token_pool_a -> new_token_pool_a in
       let new_token_pool_b =
         match is_nat (amount_in_b - brl) with
         | None -> (failwith error_B_PROTOCOL_FEE_IS_TOO_BIG : nat)
         | Some new_token_pool_b -> new_token_pool_b in
       {
         amount_in_A = new_token_pool_a;
         amount_in_B = new_token_pool_b;
         reserve_fee_in_A = arl;
         reserve_fee_in_B = brl
       })

[@inline]
let compute_out_amount (token_in : nat) (in_total : nat) (out_total : nat) (curve : curve_type) : nat =
  let b_out =
    match curve with
    | Product ->
    (token_in * out_total) /
    ((in_total * 10000n) + token_in) 
    | Flat ->
    (flat in_total out_total token_in / 10000n) in
  b_out

let compute_out_amount_when_A_or_B_is_SMAK (a_to_b : bool) (aorb_smak : a_or_b) (token_in : nat) (in_total : nat) (out_total : nat) (curve : curve_type) : (nat * nat * nat) =
  let reduce = 
    match curve with
    | Flat -> 9990n
    | Product -> 9972n in
  let total_fees = abs (10000n - reduce) in
  match aorb_smak with
  | A ->
    if a_to_b
    then
      let b_out = compute_out_amount (token_in * reduce) in_total out_total curve in
      (b_out, ((total_fees * token_in) / 10000n), 0n)
    else
      let bought_pre =
        match curve with
        | Flat -> flat (in_total * reduce) out_total token_in / 10000n
        | Product -> 
          (token_in * out_total) / (in_total + token_in) in
      (((reduce * bought_pre) / 10000n), ((total_fees * bought_pre) / 10000n), 0n)
  | B ->
    if a_to_b
    then
      let bought_pre = 
        match curve with
        | Flat -> flat (in_total * reduce) out_total token_in / 10000n
        | Product -> 
          (token_in * out_total) / (in_total + token_in) in
      (((reduce * bought_pre) / 10000n), 0n, ((total_fees * bought_pre) / 10000n))
    else
      (let b_out = compute_out_amount (token_in * reduce) in_total out_total curve in
       (b_out, 0n, ((total_fees * token_in) / 10000n)))

let withdraw_or_burn_fees (storage : storage) (reserve_fee_to_burn_A : nat) (reserve_fee_to_burn_B : nat) : operation list =
  let withdraw_or_burn_op_A =
    if
      check_tokens_are_equal (storage.token_address_a, storage.token_id_a)
        (storage.token_address_smak, FA12)
    then burn_smak storage Tezos.self_address reserve_fee_to_burn_A
    else
      token_a_transfer storage Tezos.self_address storage.reserve
        reserve_fee_to_burn_A in
  let withdraw_or_burn_op_B =
    if
      check_tokens_are_equal (storage.token_address_b, storage.token_id_b)
        (storage.token_address_smak, FA12)
    then burn_smak storage Tezos.self_address reserve_fee_to_burn_B
    else
      token_b_transfer storage Tezos.self_address storage.reserve
        reserve_fee_to_burn_B in
  opt_operation_concat withdraw_or_burn_op_A withdraw_or_burn_op_B

let get_entrypoint_A2 () : balance_of_response list contract option =
  (Tezos.get_entrypoint_opt "%fA2InternalA" Tezos.self_address : balance_of_response
       list
       contract
       option)

let get_entrypoint_A12 () : token contract option =
  (Tezos.get_entrypoint_opt "%fA12InternalA" Tezos.self_address : token
       contract
       option)

let get_entrypoint_B2 () : balance_of_response list contract option =
  (Tezos.get_entrypoint_opt "%fA2InternalB" Tezos.self_address : balance_of_response
       list
       contract
       option)

let get_entrypoint_B12 () : token contract option =
  (Tezos.get_entrypoint_opt "%fA12InternalB" Tezos.self_address : token
       contract
       option)

let update_ended_callback () : operation =
  let my_address = Tezos.self_address in
  match (Tezos.get_entrypoint_opt "%updateTokenEnded" my_address : unit
             contract
             option)
  with
  | None -> (failwith error_UPDATETOKENENDED_NOT_FOUND_IN_SELF : operation)
  | Some c -> Tezos.transaction () 0mutez c

[@inline]
let fa2_balance_callback (token_pool : fa2_update_token_pool_internal) : nat =
  match token_pool with
  | (_, amt)::[] -> amt
  | _ -> (failwith error_INVALID_FA2_BALANCE_RESPONSE : nat)

[@inline]
let update_token_pool_aux (token_id : fa_token) (token_address : address) (get_entrypoint2 : unit -> balance_of_response list contract option) (get_entrypoint12 : unit -> token contract option) : operation =
  let my_address = Tezos.self_address in
  match token_id with
  | FA2 fa2_token_id ->
    let token_balance_of : balance_of_param contract =
      get_contract_FA2_balance_of token_address in
    let cfmm_update_token_pool_internal : balance_of_response list contract =
      match get_entrypoint2 () with
      | None ->
        (failwith error_NON_EXISTING_ENTRYPOINT2 : balance_of_response list
             contract)
      | Some c -> c in
    Tezos.transaction
      {
        requests = [{ owner = my_address; token_id = fa2_token_id }];
        callback = cfmm_update_token_pool_internal
      } 0mutez token_balance_of
  | FA12 ->
    let token_get_balance : get_balance_fa12 contract =
      get_contract_FA12_get_balance token_address in
    let cfmm_update_token_pool_internal
      : fa12_update_token_pool_internal contract =
      match get_entrypoint12 () with
      | None -> (failwith error_NON_EXISTING_ENTRYPOINT12 : token contract)
      | Some c -> c in
    Tezos.transaction (my_address, cfmm_update_token_pool_internal) 0mutez
      token_get_balance

#endif