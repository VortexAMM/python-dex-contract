let set_baker (param : set_baker_param) (store : storage) : return =
    if store.self_is_updating_token_pool then
      (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.amount <> 0mutez then
       (failwith error_NO_AMOUNT_TO_BE_SENT  : return)
    else if store.freeze_baker then
        (failwith error_BAKER_PERMANENTLY_FROZEN : return)
    else if Tezos.sender <> store.manager then
        (failwith error_ONLY_MANAGER_CAN_SET_BAKER : return)
    else
        let { 
                baker = baker ;
                freeze_baker = freeze_baker 
            } = param in
        if store.token_type_a = Xtz || store.token_type_b = Xtz then 
        ([Tezos.set_delegate baker], {store with freeze_baker = freeze_baker})
        else 
            ([] : operation list), { store with freeze_baker = true }
