#if !DEX_REMOVE_LIQUIDITY
#define DEX_REMOVE_LIQUIDITY

let remove_liquidity (param : remove_liquidity) (store : storage) : return =
    let { to_ = to_ ;
          lqt_burned = lqt_burned ;
          min_xtz_withdrawn = min_xtz_withdrawn ;
          min_tokens_withdrawn = min_tokens_withdrawn ;
          deadline = deadline } = param in

    if store.self_is_updating_token_pool then
      (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.now >= deadline then
      (failwith error_THE_CURRENT_TIME_MUST_BE_LESS_THAN_THE_DEADLINE : return)
    else if Tezos.amount > 0mutez then
        (failwith error_AMOUNT_MUST_BE_ZERO : return)
    else 
        let xtz_withdrawn    : tez = natural_to_mutez ((lqt_burned * (mutez_to_natural store.xtz_pool)) / store.lqt_total) in
        let tokens_withdrawn : nat = lqt_burned * store.token_pool /  store.lqt_total in

        // Check that minimum withdrawal conditions are met
        if xtz_withdrawn < min_xtz_withdrawn then
            (failwith error_THE_AMOUNT_OF_XTZ_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_XTZ_WITHDRAWN : return)
        else if tokens_withdrawn < min_tokens_withdrawn  then
            (failwith error_THE_AMOUNT_OF_TOKENS_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN : return)
        // Proceed to form the operations and update the storage
        else 
            // calculate lqt_total, convert int to nat
            let new_lqt_total = match (is_a_nat ( store.lqt_total - lqt_burned)) with
                // This check should be unecessary, the fa12 logic normally takes care of it
                | None -> (failwith error_CANNOT_BURN_MORE_THAN_THE_TOTAL_AMOUNT_OF_LQT : nat)
                | Some n -> n in
            // Calculate token_pool, convert int to nat
            let new_token_pool = match is_a_nat (store.token_pool - tokens_withdrawn) with
                | None -> (failwith error_TOKEN_POOL_MINUS_TOKENS_WITHDRAWN_IS_NEGATIVE : nat)
                | Some n -> n in

            let op_lqt = mint_or_burn store Tezos.sender (0 - lqt_burned) in
            let op_token = token_transfer store Tezos.self_address to_ tokens_withdrawn in
            let op_xtz = xtz_transfer to_ xtz_withdrawn in
            let store = {store with xtz_pool = store.xtz_pool - xtz_withdrawn ; lqt_total = new_lqt_total ; token_pool = new_token_pool} in

            let history = Big_map.update "token_pool" (Some store.token_pool) store.history in
            let history = Big_map.update "xtz_pool" (Some (mutez_to_natural store.xtz_pool)) history in
            let user_investments = Big_map.update Tezos.sender (Some {xtz=xtz_withdrawn; token=tokens_withdrawn; direction=Remove}) store.user_investments in
            let store = { store with history = history ; user_investments = user_investments } in

            ([op_lqt; op_token; op_xtz], store)

#endif