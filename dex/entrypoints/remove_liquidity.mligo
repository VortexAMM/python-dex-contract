let remove_liquidity (param : remove_liquidity_param) (store : storage) : return =
    let () = no_xtz in
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
                error_THE_AMOUNT_OF_TOKEN_A_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN
            : return)
        else if tokens_b_withdrawn < min_token_b_withdrawn then
          (failwith
             error_THE_AMOUNT_OF_TOKEN_B_WITHDRAWN_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_WITHDRAWN
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
            let ops =
              opt_to_op_list [op_token_a_transfer; op_token_b_transfer; op_lqt_mint_or_burn] in

           if store.token_type_a = Xtz || store.token_type_b = Xtz then
                let balance_of_request = Tezos.sender in
                let lqt_address =
                  match store.lqt_address with
                  | None -> (failwith(error_LQT_ADDRESS_IS_NOT_SET) : address)
                  | Some addr -> addr in
                let user_balance = 
                  match (Tezos.call_view "balance_of_view" balance_of_request lqt_address : nat option) with
                  | None -> (failwith(error_BALANCE_OF_VIEW_RETURNED_AN_ERROR) : nat)
                  | Some user_balance -> user_balance in
               
               let new_user_balance =
                match is_a_nat (user_balance - lqt_burned) with
                  | None ->
                    (failwith error_USER_BALANCE_IS_INSUFFICIENT : nat)
                  | Some user_balance -> user_balance in

               let new_store = update_reward store in 
               let new_store = update_user_reward Tezos.sender user_balance new_user_balance new_store in 
               let new_store =
                {
                  new_store with
                  lqt_total = new_lqt_total;
                  token_pool_a = new_pool_a;
                  token_pool_b = new_pool_b;

                } in
              ops, new_store
           else 
                 let new_store =
                {
                  store with
                  lqt_total = new_lqt_total;
                  token_pool_a = new_pool_a;
                  token_pool_b = new_pool_b;

                } in
          ops, new_store