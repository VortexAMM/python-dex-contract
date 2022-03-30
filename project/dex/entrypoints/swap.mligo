let swap (param : swap_param) (store : storage) : return =
    let {
        t2t_to;
        tokens_sold;
        min_tokens_bought;
        a_to_b;
        deadline;
        } = param in
    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL : return)
    else if Tezos.now > deadline then
        (failwith error_SWAP_DEADLINE_IS_OVER : return)
    else if (a_to_b && store.token_type_a = Xtz && Tezos.amount = 0mutez) ||
        (not a_to_b && store.token_type_b = Xtz && Tezos.amount = 0mutez) then
            (failwith error_AMOUNT_MUST_BE_SENT : return)
    else if (a_to_b && store.token_type_a <> Xtz && Tezos.amount <> 0mutez) ||
        (not a_to_b && store.token_type_b <> Xtz && Tezos.amount <> 0mutez) then
            (failwith error_NO_AMOUNT_TO_BE_SENT : return)
    else
        let (in_total, in_type, out_total, out_type) =
            if a_to_b then
                (
                    store.token_pool_a,
                    store.token_type_a,
                    store.token_pool_b, 
                    store.token_type_b
                )
            else
                (
                    store.token_pool_b,
                    store.token_type_b,
                    store.token_pool_a,
                    store.token_type_a
                ) 
            in


    let burn_amount = tokens_sold * 2n / 10_000n in
    let reserve_amount = tokens_sold / 10_000n in
    let total_fees_in = burn_amount + reserve_amount in
    let reduced_sold = 
        match store.curve with
        | Flat -> tokens_sold * 9990n / 10_000n
        | Product -> tokens_sold * 9972n / 10_000n
    in
    let bought = 
            (compute_out_amount
                reduced_sold
                in_total
                out_total
                store.curve)
                in

    if bought < min_tokens_bought then
        (failwith error_TOKENS_BOUGHT_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_BOUGHT : return)
    else
        let (new_pool_a, new_pool_b) =
            if a_to_b then
                (* A to B *)
                ( store.token_pool_a + tokens_sold - total_fees_in,
                  store.token_pool_b - bought )
            else
                (* B to A *)
                ( store.token_pool_a - bought,
                  store.token_pool_b + tokens_sold - total_fees_in) 
            in
        let new_pool_a =
            match is_nat new_pool_a with
            | None ->
                (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : nat)
            | Some difference -> difference in
        let new_pool_b =
            match is_nat new_pool_b with
            | None ->
                (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : nat)
            | Some difference -> difference in
        let op_token_in_transfer =
            make_transfer
                in_type
                Tezos.sender
                Tezos.self_address
                tokens_sold
            in
        let ops_token_out_transfer = 
            if Tezos.sender = store.sink && out_type = store.token_type_smak then
                let reward = bought * store.sink_reward_rate / 10_000n in 
                [
                    make_transfer
                        out_type
                        Tezos.self_address
                        t2t_to
                        reward
                    ;
                    make_transfer
                        out_type
                        Tezos.self_address
                        null_implicit_account
                        (abs (bought - reward))
                ]
            else 
                [
                    make_transfer
                        out_type
                        Tezos.self_address
                        t2t_to
                        bought
                ]
            in

        let ops = 
            opt_to_op_list (
                deposit_smak
                    store
                    in_type
                    burn_amount
                    reserve_amount
                    out_type
                    a_to_b
                )
            in

        let ops = List.fold (
            fun(l, op : operation list * operation) -> 
            op :: l) 
            ops (opt_to_op_list ops_token_out_transfer)
            in
        let ops = 
            match op_token_in_transfer with
            | None -> ops
            | Some op -> op :: ops in
        let new_store =
            {
                store with
                token_pool_a = new_pool_a;
                token_pool_b = new_pool_b;
            } 
            in
        ops, new_store