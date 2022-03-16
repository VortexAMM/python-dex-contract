let remove_liquidity (param : remove_liquidity_param) (store : storage) : return =
      let {
      rem_to = to_;
      lqt_burned;
      min_token_a_withdrawn;
      min_token_b_withdrawn;
      deadline;
    } = param in
    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL : return)
    else if Tezos.now > deadline then
        (failwith error_REMOVE_LIQUIDITY_DEADLINE_IS_OVER : return)
    else
        let tokens_a_withdrawn : nat =
          lqt_burned * store.token_pool_a / store.lqt_total in
        let tokens_b_withdrawn : nat =
          lqt_burned * store.token_pool_b / store.lqt_total in
        
        if tokens_a_withdrawn < min_token_a_withdrawn then
            (failwith
                error_THE_AMOUNT_OF_TOKENS_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN
            : return)
        else if tokens_b_withdrawn < min_token_b_withdrawn then
          (failwith
             error_THE_AMOUNT_OF_TOKENS_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN
            : return)
        else
            let new_lqt_total =
                match is_a_nat (store.lqt_total - lqt_burned) with
                | None ->
                    (failwith error_CANNOT_BURN_MORE_THAN_THE_TOTAL_AMOUNT_OF_LQT
                      : nat)
                | Some n -> n in
            let new_pool_a : nat =
                match is_a_nat (store.token_pool_a - tokens_a_withdrawn) with
                | None ->
                    (failwith error_TOKEN_POOL_MINUS_TOKENS_WITHDRAWN_IS_NEGATIVE
                      : nat)
                | Some n -> n in
            let new_pool_b : nat =
                match is_a_nat (store.token_pool_b - tokens_b_withdrawn) with
                | None ->
                    (failwith error_TOKEN_POOL_MINUS_TOKENS_WITHDRAWN_IS_NEGATIVE
                      : nat)
                | Some n -> n in
            let new_history =
              Big_map.update "token_pool_a" (Some new_pool_a) store.history in
            let new_history =
              Big_map.update "token_pool_b" (Some new_pool_b) new_history in
            
            let new_user_investments =
                let invest =
                  {
                    token_invest_a = tokens_a_withdrawn;
                    token_invest_b = tokens_b_withdrawn;
                    direction = Remove;
                  } in
                Big_map.update
                  Tezos.sender
                  (Some invest)
                  store.user_investments in

            let op_lqt_mint_or_burn =
                mint_or_burn store Tezos.sender (0 - lqt_burned) in
            let op_token_b_transfer =
                make_transfer
                    store.token_type_b
                    Tezos.self_address
                    to_
                    tokens_b_withdrawn
            in
            let op_token_a_transfer =
                make_transfer
                    store.token_type_a
                    Tezos.self_address
                    to_
                    tokens_a_withdrawn
            in

            let new_store =
                {
                  store with
                  lqt_total = new_lqt_total;
                  token_pool_a = new_pool_a;
                  token_pool_b = new_pool_b;
                  history = new_history;
                  user_investments = new_user_investments;
                  last_k = new_pool_a * new_pool_b;
                } in
            let ops_opt = [op_token_a_transfer; op_token_b_transfer; op_lqt_mint_or_burn] in
            (opt_to_op_list ops_opt), new_store