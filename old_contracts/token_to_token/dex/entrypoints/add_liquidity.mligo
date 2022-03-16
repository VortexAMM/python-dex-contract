#if !DEX_ADD_LIQUIDITY
#define DEX_ADD_LIQUIDITY

let add_liquidity (param : add_liquidity) (storage : storage) : result =
  let { owner; amount_token_a; min_lqt_minted; max_tokens_deposited; deadline }
    = param in
  let () = check_self_is_not_updating_token_pool storage in
  let () = check_deadline deadline in
  let tokens_b_deposited : nat =
    (amount_token_a * storage.token_pool_b) / storage.token_pool_a in
  let lqt_a = (amount_token_a * storage.lqt_total) / storage.token_pool_a in
  let lqt_b = (tokens_b_deposited * storage.lqt_total) / storage.token_pool_b in
  let lqt_minted : nat = if lqt_a <= lqt_b then lqt_a else lqt_b in
  if tokens_b_deposited > max_tokens_deposited
  then
    (failwith
       error_MAX_TOKENS_DEPOSITED_MUST_BE_GREATER_THAN_OR_EQUAL_TO_TOKENS_DEPOSITED : 
       result)
  else
  if lqt_minted < min_lqt_minted
  then
    (failwith error_LQT_MINTED_MUST_BE_GREATER_THAN_MIN_LQT_MINTED : 
       result)
  else
    (let new_lqt_total : nat = storage.lqt_total + lqt_minted in
     let new_pool_a : nat = storage.token_pool_a + amount_token_a in
     let new_pool_b : nat = storage.token_pool_b + tokens_b_deposited in
     let new_history : history_big_map =
       Big_map.update "token_pool_b" (Some new_pool_b) storage.history in
     let new_history : history_big_map =
       Big_map.update "token_pool_a" (Some new_pool_a) new_history in
     let new_user_investments : user_investments_big_map =
       let invest =
         {
           token_invest_a = amount_token_a;
           token_invest_b = tokens_b_deposited;
           direction = ADD
         } in
       Big_map.update Tezos.sender (Some invest) storage.user_investments in
     let storage : storage =
       {
         storage with
         lqt_total = new_lqt_total;
         token_pool_a = new_pool_a;
         token_pool_b = new_pool_b;
         history = new_history;
         user_investments = new_user_investments;
         last_k = (new_pool_a * new_pool_b)
       } in
     let op_token_a_transfer : operation option =
       token_a_transfer storage Tezos.sender Tezos.self_address
         amount_token_a in
     let op_token_b_transfer : operation option =
       token_b_transfer storage Tezos.sender Tezos.self_address
         tokens_b_deposited in
     let op_lqt_mint_or_burn : operation list =
       mint_or_burn storage owner (int lqt_minted) in
     ((operation_concat
         (opt_operation_concat op_token_a_transfer op_token_b_transfer)
         op_lqt_mint_or_burn), storage))

#endif