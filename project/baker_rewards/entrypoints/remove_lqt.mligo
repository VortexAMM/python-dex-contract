let remove_lqt (param : remove_lqt_param) (store : storage) : return =
    if Tezos.sender <> store.dex_address then
        (failwith(error_ONLY_DEX_CAN_CALL) : return)
    else
        let new_counter = store.counter + 1n in
        let old_provider_data =
            match Big_map.find_opt Tezos.source store.providers with
            | None -> 
                (failwith(error_NO_LQT_OWNED) : provider_data)
            | Some data -> data in
            let new_lqt_shares =
                match is_a_nat (old_provider_data.lqt_shares - param) with
                | None -> (failwith(error_REMOVED_LQT_IS_GREATER_THAN_LQT_OWNED) : nat)
                | Some n -> n in
            let new_provider_data =
                {old_provider_data with
                    counter = new_counter;
                    lqt_shares = new_lqt_shares;
                } in
        let new_total = 
            match is_a_nat (store.total_lp_tokens - param) with
            | None -> (failwith(error_REMOVED_LQT_IS_GREATER_THAN_TOTAL_LQT))
            | Some total -> total in
        let new_providers = Big_map.update Tezos.source (Some new_provider_data) store.providers in
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