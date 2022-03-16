let deposit_fees (store : storage) : return =
    if Tezos.sender <> store.dex_address then
        (failwith(error_ONLY_DEX_CAN_CALL) : return)
    else 
        let current_history_data =
            match Big_map.find_opt store.counter store.lqt_history with
            | None -> (failwith("no current history") : history)
            | Some entry -> entry in
        let new_history_data = 
            { current_history_data with total_fees = current_history_data.total_fees + Tezos.amount;
            } in
        let new_history = Big_map.update store.counter (Some new_history_data) store.lqt_history in
        let new_store = { store with lqt_history = new_history } in
        ([] : operation list), new_store