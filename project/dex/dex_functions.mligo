#include "../common/functions.mligo"


// [@inline]
// let a_or_b_is_SMAK (store : storage) : a_or_b option =
//   if
//     check_tokens_equal
//       store.token_type_smak
//       store.token_type_a
//   then Some A
//   else if
//     check_tokens_equal
//       store.token_type_smak
//       store.token_type_b
//   then Some B
//   else None

// [@inline]
// let burn_smak (store : storage) (token_amount : nat) (token_to_burn_type : token_type) : operation list =
//   if check_tokens_equal
//     token_to_burn_type
//     store.token_type_smak then
//       opt_to_op_list
//         [make_transfer
//           token_to_burn_type
//           Tezos.self_address
//           null_implicit_account
//           token_amount
//           ]
//   else
//     let sink_contr =
//       match (Tezos.get_entrypoint_opt "%burn" store.reserve : sink_burn_param contract option) with
//       | None -> (failwith error_NO_SINK_CONTRACT_EXISTS : sink_burn_param contract)
//       | Some contr -> contr in
//     let amount_to_send = 
//       if token_to_burn_type = Xtz then Tezos.amount else 0mutez in
//     let burn_param =
//     {
//       token_to_burn_type = token_to_burn_type;
//       to_burn = token_amount;
//       min_to_burn = 0n;
//       swap_direction = true;
//       deadline = Tezos.now + 1_000_000;
//     } in
//     let ops =
//       match 
//         (make_transfer
//           token_to_burn_type
//           Tezos.self_address
//           store.sink
//           token_amount) with
//           | None -> 
//     Tezos.transaction burn_param amount_to_send sink_contr

[@inline]
let mint_or_burn (store : storage) (target : address) (quantity : int) :
    operation option =
  if quantity = 0 then 
    None
  else
    let lqt_admin : mint_or_burn contract =
      let lqt_address =
        match store.lqt_address with
        | None -> (failwith error_LQT_ADDRESS_IS_NOT_SET : address)
        | Some lqt_address -> lqt_address
      in
      match
        (Tezos.get_entrypoint_opt "%mintOrBurn" lqt_address
          : mint_or_burn contract option)
      with
      | None ->
          (failwith error_LQT_CONTRACT_MUST_HAVE_A_MINT_OR_BURN_ENTRYPOINT
            : mint_or_burn contract)
      | Some contract -> contract
    in
    Some (Tezos.transaction {quantity = quantity; target = target} 0mutez lqt_admin)

[@inline]
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


[@inline]
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
let compute_out_amount (token_in : nat) (in_total : nat) (out_total : nat) (curve : curve_type) : nat =
  let b_out =
    match curve with
    | Product ->
    (token_in * out_total) /
    ((in_total) + token_in) 
    | Flat ->
    (flat in_total out_total token_in) in
  b_out


// [@inline]
// let compute_out_amount_when_A_or_B_is_SMAK (a_to_b : bool) (aorb_smak : a_or_b) (token_in : nat) (in_total : nat) (out_total : nat) (curve : curve_type) : (nat * nat * nat) =
//   let reduce = 
//     match curve with
//     | Flat -> 9990n
//     | Product -> 9972n in
//   let total_fees = abs (10000n - reduce) in
//   match aorb_smak with
//   | A ->
//     if a_to_b
//     then
//       let b_out = compute_out_amount (token_in * reduce) in_total out_total curve in
//       (b_out, ((total_fees * token_in) / 10000n), 0n)
//     else
//       let bought_pre =
//         match curve with
//         | Flat -> flat (in_total * reduce) out_total token_in / 10000n
//         | Product -> 
//           (token_in * out_total) / (in_total + token_in) in
//       (((reduce * bought_pre) / 10000n), ((total_fees * bought_pre) / 10000n), 0n)
//   | B ->
//     if a_to_b
//     then
//       let bought_pre = 
//         match curve with
//         | Flat -> flat (in_total * reduce) out_total token_in / 10000n
//         | Product -> 
//           (token_in * out_total) / (in_total + token_in) in
//       (((reduce * bought_pre) / 10000n), 0n, ((total_fees * bought_pre) / 10000n))
//     else
//       (let b_out = compute_out_amount (token_in * reduce) in_total out_total curve in
//        (b_out, 0n, ((total_fees * token_in) / 10000n)))

(** Create operations to either withdraw (when the token is not the
   SMAK token) or burn (when the token is the SMAK token) the
   tokens. *)
// let withdraw_or_burn_fees (store : storage) (reserve_fee_to_burn_A : nat)
//     (reserve_fee_to_burn_B : nat) : operation list =
//   let withdraw_or_burn_op_A =
//   burn_smak store reserve_fee_to_burn_A store.token_type_a
//   in
//   let withdraw_or_burn_op_B =
//     (* send B to sink, to burn or exchange to SMAK and burn *)
//     burn_smak store reserve_fee_to_burn_B store.token_type_b
//   in
//     [withdraw_or_burn_op_A; withdraw_or_burn_op_B]

// let compute_fees (store : storage) (amount_in_a : nat) (amount_in_b : nat)
//     (feeSMAK_A : nat) (feeSMAK_B : nat) : amounts_and_fees =
//   match a_or_b_is_SMAK store with
//   | Some _ ->
//       (* A or B is SMAK: no Uniswap-like adjustments to make *)
//       {
//         amount_in_A = amount_in_a;
//         amount_in_B = amount_in_b;
//         reserve_fee_in_A = feeSMAK_A;
//         reserve_fee_in_B = feeSMAK_B;
//       }
//   | None -> (
//       (* Neither A nor B is the SMAK token: See Uniswapv2 whitepaper
//          or working document to explain these computations *)
//       let k1 = store.last_k in
//       let k2 = amount_in_a * amount_in_b in
//       let sqr1 = sqrt k1 in
//       let sqr2 = sqrt k2 in
//       match is_a_nat (sqr2 - sqr1) with
//       | None ->
//           (failwith error_K2_SHOULD_BE_GREATER_THAN_K1 : amounts_and_fees)
//       | Some sq2minussq1 ->
//           let sm =
//             (* stillborn, protocol-fee, Uniswap-minted shares  *)
//             sq2minussq1 * store.lqt_total / (ceildiv (25n * sqr2) 3n + sqr1)
//           in
//           (* new reserve fee to "burn" in A *)
//           let arl = sm * amount_in_a / (store.lqt_total + sm) in
//           (* new reserve fee to "burn" in B *)
//           let brl = sm * amount_in_b / (store.lqt_total + sm) in
//           let new_token_pool_a =
//             match is_nat (amount_in_a - arl) with
//             | None -> (failwith error_A_PROTOCOL_FEE_IS_TOO_BIG : nat)
//             | Some new_token_pool_a -> new_token_pool_a
//           in
//           let new_token_pool_b =
//             match is_nat (amount_in_b - brl) with
//             | None -> (failwith error_B_PROTOCOL_FEE_IS_TOO_BIG : nat)
//             | Some new_token_pool_b -> new_token_pool_b
//           in
//           {
//             amount_in_A = new_token_pool_a;
//             amount_in_B = new_token_pool_b;
//             reserve_fee_in_A = arl;
//             reserve_fee_in_B = brl;
//           })


[@inline]
let get_contract_FA2_balance_of (token_address : address) : balance_of_param contract =
  match (Tezos.get_entrypoint_opt "%balance_of" token_address : balance_of_param contract option) with
  | None ->
    (failwith error_INVALID_FA2_TOKEN_CONTRACT_MISSING_BALANCE_OF : balance_of_param contract)
  | Some contract -> contract


[@inline]
let get_contract_FA12_get_balance (token_address : address) : get_balance_fa12 contract =
  match (Tezos.get_entrypoint_opt "%getBalance" token_address : get_balance_fa12 contract option) with
  | None ->
    (failwith error_INVALID_FA12_TOKEN_CONTRACT_MISSING_GETBALANCE : get_balance_fa12 contract)
  | Some contract -> contract

[@inline]
let fa2_balance_callback (token_pool : fa2_update_token_pool_internal) : nat =
  match token_pool with
  | (_, amt)::[] -> amt
  | _ -> (failwith error_INVALID_FA2_BALANCE_RESPONSE : nat)

[@inline]
let update_token_pool_internal_checks (token_address : address) (store : storage) : unit =
  if
    (not store.self_is_updating_token_pool) ||
    (Tezos.sender <> token_address)
  then
    (failwith
       error_THIS_ENTRYPOINT_MAY_ONLY_BE_CALLED_BY_GETBALANCE_OF_TOKENADDRESS : 
       unit)
  else if Tezos.amount <> 0mutez then
    failwith error_NO_AMOUNT_TO_BE_SENT
  else ()


let deposit_smak (store : storage) (type_to_burn : token_type) (burn_amount : nat) (reserve_amount : nat) (reference_token: token_type) (direction : bool) : operation option list =
  if burn_amount = 0n && reserve_amount = 0n then
    ([] : operation option list)
  else 
      let sink_deposit =
          match (Tezos.get_entrypoint_opt "%deposit" store.sink : sink_deposit_params contract option) with
          | None -> (failwith error_NO_SINK_DEPOSIT_ENTRYPOINT_EXISTS : sink_deposit_params contract)
          | Some contr -> contr in
      let deposit_params =
      {
          token_to_deposit = type_to_burn;
          reference_token = reference_token;
          burn_amount = burn_amount;
          reserve_amount = reserve_amount;
          direction = direction;
      } in
      let xtz_to_deposit =
        if type_to_burn = Xtz then
          natural_to_mutez (burn_amount + reserve_amount)
        else
          0mutez in
      let opt_op_transfer =
        if type_to_burn = Xtz then 
          (None : operation option)
        else
          make_transfer
              type_to_burn
              Tezos.self_address
              store.sink
              (burn_amount + reserve_amount)
          in
      let opt_op_deposit =
        Some
          (Tezos.transaction
            deposit_params
            xtz_to_deposit
            sink_deposit)
        in

      [opt_op_transfer; opt_op_deposit]