let set_lqt_address (param : set_lqt_address_param) (store : storage) : return =
    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL : return)
    else if Tezos.sender <> store.manager then
        (failwith error_ONLY_MANAGER_CAN_SET_LIQUIDITY_ADDRESS : return)
    else
        match store.lqt_address with
        | None ->
            (([] : operation list), {store with lqt_address = Some param})
        | Some _ -> (failwith error_LQT_ADDRESS_ALREADY_SET : return)