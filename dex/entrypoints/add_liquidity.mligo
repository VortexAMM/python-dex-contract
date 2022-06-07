let add_liquidity (param : add_liquidity_param) (store : storage) = 
    let {owner; amount_token_a; min_lqt_minted; max_tokens_deposited; deadline;} =
        param in
    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL : return)
    else if Tezos.now > deadline then
        (failwith error_ADD_LIQUIDITY_DEADLINE_IS_OVER : return)
    else
        let amount_token_b =
            match store.curve with
            | Product -> amount_token_a * store.token_pool_b / store.token_pool_a
            | Flat -> amount_token_a * store.token_pool_a / store.token_pool_b in

        if store.token_type_a = Xtz && mutez_to_natural Tezos.amount <> amount_token_a then
            (failwith(error_INCORRECT_XTZ_AMOUNT_WAS_SENT) : return)
        else if store.token_type_b = Xtz && mutez_to_natural Tezos.amount < amount_token_b then
            (failwith(error_INCORRECT_XTZ_AMOUNT_WAS_SENT) : return)
        else if store.token_type_a <> Xtz && store.token_type_b <> Xtz && Tezos.amount <> 0mutez then
            (failwith(error_NO_AMOUNT_TO_BE_SENT) : return)
        else
            let lqt_a = amount_token_a * store.lqt_total / store.token_pool_a in
            let lqt_b = amount_token_b * store.lqt_total / store.token_pool_b in
            let lqt_minted = 
                if lqt_a <= lqt_b then
                    lqt_a
                else
                    lqt_b in
            if amount_token_b > max_tokens_deposited then
                (failwith error_MAX_TOKENS_DEPOSITED_MUST_BE_GREATER_THAN_OR_EQUAL_TO_TOKENS_DEPOSITED : return)
            else if lqt_minted < min_lqt_minted then
                (failwith error_LQT_MINTED_MUST_BE_GREATER_THAN_MIN_LQT_MINTED : return)
            else
                let new_lqt_total = lqt_minted + store.lqt_total in
                let new_pool_a = amount_token_a + store.token_pool_a in
                let new_pool_b = amount_token_b + store.token_pool_b in

                let op_token_a_transfer =
                    make_transfer
                        store.token_type_a
                        Tezos.sender
                        Tezos.self_address
                        amount_token_a
                in
                let op_token_b_transfer =
                    make_transfer
                        store.token_type_b
                        Tezos.sender
                        Tezos.self_address
                        amount_token_b
                in 
                let op_lqt_mint_or_burn =
                    mint_or_burn store owner (int lqt_minted) in

                let ops = opt_to_op_list [op_token_a_transfer; op_token_b_transfer; op_lqt_mint_or_burn] in

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

                        let new_user_balance =  user_balance + lqt_minted in

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