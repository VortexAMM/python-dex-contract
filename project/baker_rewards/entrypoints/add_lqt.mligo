let add_lqt (param : add_lqt_param) (store : storage) : return =
    if Tezos.sender <> store.dex_address then
        (failwith(error_ONLY_DEX_CAN_CALL) : return)
    else
        let old_provider_data =
            match Big_map.find_opt param.owner store.providers with
            | None -> 
                {
                    counter = store.counter;
                    lqt_shares = 0n;
                    accumulated = 0mutez;
                }
            | Some data ->
                data in
        let new_total = store.total_lp_tokens + param.lqt_minted in
        let new_acc =
            if old_provider_data.lqt_shares <> 0n then 
                calculate_rewards old_provider_data store.counter store
            else
                0mutez in
        let new_counter = store.counter + 1n in
        let new_provider_data =
            {
                counter = new_counter;
                lqt_shares = old_provider_data.lqt_shares + param.lqt_minted;
                accumulated = new_acc;
            } in
        let new_providers = Big_map.update param.owner (Some new_provider_data) store.providers in
        let new_history_entry =
            {
                total_lqt = new_total;
                total_fees = 0mutez;
            } in
        let new_history = Big_map.update new_counter (Some new_history_entry) store.lqt_history in
        let new_store =
            { store with
                total_lp_tokens = new_total;
                counter = new_counter;
                providers = new_providers;
                lqt_history = new_history;
            } in
        ([] : operation list), new_store