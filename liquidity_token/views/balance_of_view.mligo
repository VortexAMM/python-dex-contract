[@view] let balance_of_view (param, store : address * storage) : nat =
    match Big_map.find_opt param store.tokens with
    | Some value -> value
    | None -> 0n