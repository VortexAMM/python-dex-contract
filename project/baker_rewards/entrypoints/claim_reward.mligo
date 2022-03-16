let claim_reward (reward_to : address) (store : storage) : return =
    let new_counter = store.counter + 1n in
    let old_provider_data =
        match Big_map.find_opt Tezos.source store.providers with
        | None ->  (failwith(error_NO_LQT_OWNED) : provider_data)
        | Some data -> data in
    let reward_to_contract =
        match (Tezos.get_contract_opt reward_to : unit contract option) with
        | None -> (failwith("no reward to contract") : unit contract)
        | Some contr -> contr in
    let reward =
        if old_provider_data.lqt_shares <> 0n then
            calculate_rewards old_provider_data store.counter store
        else 0mutez in
    let ops = 
        if reward = 0mutez then 
            ([] : operation list)
        else if Tezos.balance < reward then
            (failwith(error_REWARD_LARGER_THAN_BALANCE) : operation list)
        else
            [Tezos.transaction () reward reward_to_contract] in
    let new_provider_data =
        {
            counter = new_counter;
            accumulated = 0mutez;
            lqt_shares = old_provider_data.lqt_shares;
        } in
    let new_providers = Big_map.update Tezos.source (Some new_provider_data) store.providers in
    let new_history_entry =
            {
                total_lqt = store.total_lp_tokens;
                total_fees = 0mutez;
            } in
    let new_history = Big_map.update new_counter (Some new_history_entry) store.lqt_history in
    let new_store =
        { store with
            counter = new_counter;
            lqt_history = new_history;
            providers = new_providers;
        } in
    ops, new_store