#if !DEX_REMOVE_LIQUIDITY
#define DEX_REMOVE_LIQUIDITY

let remove_liquidity (param : remove_liquidity) (storage : storage) : result =
  let { to_; lqt_burned; min_token_a_withdrawn; min_token_b_withdrawn; 
        deadline }
    = param in
  let () = check_self_is_not_updating_token_pool storage in
  let () = check_deadline deadline in
  let tokens_a_withdrawn : nat =
    (lqt_burned * storage.token_pool_a) / storage.lqt_total in
  let tokens_b_withdrawn : nat =
    (lqt_burned * storage.token_pool_b) / storage.lqt_total in
  if tokens_a_withdrawn < min_token_a_withdrawn
  then
    (failwith
       error_THE_AMOUNT_OF_TOKENS_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN : 
       result)
  else
  if tokens_b_withdrawn < min_token_b_withdrawn
  then
    (failwith
       error_THE_AMOUNT_OF_TOKENS_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN : 
       result)
  else
    (let new_lqt_total : nat =
       match is_a_nat (storage.lqt_total - lqt_burned) with
       | None ->
         (failwith error_CANNOT_BURN_MORE_THAN_THE_TOTAL_AMOUNT_OF_LQT : 
            nat)
       | Some n -> n in
     let new_pool_a : nat =
       match is_a_nat (storage.token_pool_a - tokens_a_withdrawn) with
       | None ->
         (failwith error_TOKEN_POOL_MINUS_TOKENS_WITHDRAWN_IS_NEGATIVE : 
            nat)
       | Some n -> n in
     let new_pool_b : nat =
       match is_a_nat (storage.token_pool_b - tokens_b_withdrawn) with
       | None ->
         (failwith error_TOKEN_POOL_MINUS_TOKENS_WITHDRAWN_IS_NEGATIVE : 
            nat)
       | Some n -> n in
     let new_history =
       Big_map.update "token_pool_a" (Some new_pool_a) storage.history in
     let new_history =
       Big_map.update "token_pool_b" (Some new_pool_b) new_history in
     let new_user_investments =
       let invest =
         {
           token_invest_a = tokens_a_withdrawn;
           token_invest_b = tokens_b_withdrawn;
           direction = REMOVE
         } in
       Big_map.update Tezos.sender (Some invest) storage.user_investments in
     let op_lqt_mint_or_burn : operation list =
       mint_or_burn storage Tezos.sender (0 - lqt_burned) in
     let op_token_b_transfer : operation option =
       token_b_transfer storage Tezos.self_address to_ tokens_b_withdrawn in
     let op_token_a_transfer : operation option =
       token_a_transfer storage Tezos.self_address to_ tokens_a_withdrawn in
     let storage =
       {
         storage with
         lqt_total = new_lqt_total;
         token_pool_a = new_pool_a;
         token_pool_b = new_pool_b;
         history = new_history;
         user_investments = new_user_investments;
         last_k = (new_pool_a * new_pool_b)
       } in
     ((operation_concat op_lqt_mint_or_burn
         (opt_operation_concat op_token_b_transfer op_token_a_transfer)),
      storage))

#endif