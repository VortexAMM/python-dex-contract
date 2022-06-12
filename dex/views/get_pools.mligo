[@view] let get_pools ((), store : unit * storage) : nat * nat * nat =
    store.lqt_total, store.token_pool_a, store.token_pool_b