#if !DEX_SWAP
#define DEX_SWAP

let swap (param : token_to_token) (storage : storage) =
  let { to = t2t_to; tokens_sold; min_tokens_bought; a_to_b; deadline } = param in
let () = check_self_is_not_updating_token_pool storage in
let () = check_deadline deadline in
let aorb_is_smak = a_or_b_is_SMAK storage in
let (bought, feeA_SMAK, feeB_SMAK) =
  match aorb_is_smak with
  | Some aorb_is_smak ->
    compute_out_amount_when_A_or_B_is_SMAK a_to_b aorb_is_smak tokens_sold 
      (if a_to_b then storage.token_pool_a else storage.token_pool_b)
      (if a_to_b then storage.token_pool_b else storage.token_pool_a)
      storage.curve
  | None ->
    let reduce = match storage.curve with
    | Flat -> 9990n
    | Product -> 9972n in
    if a_to_b
    then
      ((compute_out_amount (tokens_sold * reduce) storage.token_pool_a
          storage.token_pool_b storage.curve), 0n, 0n)
    else
      ((compute_out_amount (tokens_sold * reduce) storage.token_pool_b
          storage.token_pool_a storage.curve), 0n, 0n) in
if bought < min_tokens_bought
then
  (failwith
     error_TOKENS_BOUGHT_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_BOUGHT : 
     (operation list * storage))
else
  (let (new_pool_a, new_pool_b) =
     if a_to_b
     then
       (((storage.token_pool_a + tokens_sold) - feeA_SMAK),
        ((storage.token_pool_b - bought) - feeB_SMAK))
     else
       (((storage.token_pool_a - bought) - feeA_SMAK),
        ((storage.token_pool_b + tokens_sold) - feeB_SMAK)) in
   let new_pool_a : nat =
     match is_nat new_pool_a with
     | None ->
       (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : 
          nat)
     | Some difference -> difference in
   let new_pool_b =
     match is_nat new_pool_b with
     | None ->
       (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : 
          nat)
     | Some difference -> difference in
   let (op_token_a_transfer, op_token_b_transfer) =
     if a_to_b
     then
       ((token_a_transfer storage Tezos.sender Tezos.self_address tokens_sold),
        (token_b_transfer storage Tezos.self_address t2t_to bought))
     else
       ((token_a_transfer storage Tezos.self_address t2t_to bought),
        (token_b_transfer storage Tezos.sender Tezos.self_address
           tokens_sold)) in
   let op_token_transfer =
     opt_operation_concat op_token_a_transfer op_token_b_transfer in
   let new_history =
     Big_map.update "token_pool_a" (Some new_pool_a) storage.history in
   let new_history =
     Big_map.update "token_pool_b" (Some new_pool_b) new_history in
   let amounts_and_fees_out =
     compute_fees storage new_pool_a new_pool_b feeA_SMAK feeB_SMAK in
   let ops_pay_fees =
     withdraw_or_burn_fees storage amounts_and_fees_out.reserve_fee_in_A
       amounts_and_fees_out.reserve_fee_in_B in
   let storage =
     {
       storage with
       token_pool_a = amounts_and_fees_out.amount_in_A;
       token_pool_b = amounts_and_fees_out.amount_in_B;
       history = new_history;
       last_k =
         (amounts_and_fees_out.amount_in_A * amounts_and_fees_out.amount_in_B)
     } in
   ((operation_concat op_token_transfer ops_pay_fees), storage))

#endif