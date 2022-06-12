[@view] let get_dex_by_index (index, store : nat * storage) : address =
    match Big_map.find_opt index store.pools with
    | None -> (failwith(error_NO_POOL_WITH_CHOSEN_INDEX) : address) // 140
    | Some pool -> pool