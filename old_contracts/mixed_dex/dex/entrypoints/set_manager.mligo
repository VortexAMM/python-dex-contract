#if !DEX_SET_MANAGER
#define DEX_SET_MANAGER

let set_manager (new_manager : address) (store : storage) : return =
    if store.self_is_updating_token_pool then
      (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.amount > 0mutez then
        (failwith error_AMOUNT_MUST_BE_ZERO : return)
    else if Tezos.sender <> store.manager then
        (failwith error_ONLY_MANAGER_CAN_SET_MANAGER : return)
    else
        (([] : operation list), {store with manager = new_manager})

#endif