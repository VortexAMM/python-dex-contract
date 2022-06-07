let claim_reward (reward_to : address) (store : storage) : return =
    if store.token_type_a <> Xtz && store.token_type_b <> Xtz then
        (failwith(error_NO_REWARDS_FOR_THIS_PAIR) : return)
    else
        let lqt_address =
            match store.lqt_address with
            | None -> (failwith(error_LQT_ADDRESS_IS_NOT_SET) : address)
            | Some addr -> addr in
        let user_balance = 
            match (Tezos.call_view "balance_of_view" Tezos.sender lqt_address : nat option) with
            | None -> (failwith "View returned an error" : nat)
            | Some user_balance -> user_balance in

        let new_store = update_reward store in 
        let new_store = update_user_reward Tezos.sender user_balance user_balance new_store in 
        let user_reward_info = get_user_reward_info Tezos.sender new_store in
        let reward = user_reward_info.reward / accurancy_multiplier in 
        let new_reward_paid = store.reward_paid + reward in

        let ops =
            if reward = 0n then 
                ([] : operation list)
            else if reward > (mutez_to_natural Tezos.balance) then
                (failwith(error_REWARD_LARGER_THAN_BALANCE) : operation list)
            else 
                [Tezos.transaction () (natural_to_mutez reward) (get_contract_tez_to reward_to)] in

        let new_user_reward_info =
                { user_reward_info with
                    reward = 0n;
                } in
        let new_user_rewards = Big_map.update Tezos.sender (Some new_user_reward_info) store.user_rewards in
        let new_store = { new_store with user_rewards  = new_user_rewards; reward_paid = new_reward_paid; } in 
        ops, new_store