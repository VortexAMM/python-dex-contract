#if !DEX_DEFAULT
#define DEX_DEFAULT

// entrypoint to allow depositing funds
let default_ (store : storage) : return =
    // update xtz_pool
    if (store.self_is_updating_token_pool) then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE: return)
    else
        let store = {store with xtz_pool = store.xtz_pool + Tezos.amount } in
        (([] : operation list), store)

#endif