let update_claim_limit (new_limit : nat) (store : storage) : return =
    if Tezos.sender <> store.factory_address then
        (failwith(error_ONLY_FACTORY_CAN_SET_CLAIM_LIMIT) : return)
    else
        ([] : operation list), { store with token_claim_limit = new_limit}