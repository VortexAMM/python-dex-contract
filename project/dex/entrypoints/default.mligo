let default (store : storage) : return =
    if store.token_type_a <> Xtz && store.token_type_b <> Xtz then
        (failwith(error_NO_AMOUNT_TO_BE_SENT) : return)
    else
        let new_reward = (mutez_to_natural Tezos.amount) in 
        let new_store =
            {
                store with
                reward = new_reward;
            } in           
        let new_store = update_reward new_store in 
        ([] : operation list), new_store
        

