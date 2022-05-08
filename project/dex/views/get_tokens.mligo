[@view] let get_tokens ((), store : unit * storage) : token_type * token_type * address =
    match store.lqt_address with
    | None -> (failwith(error_LQT_ADDRESS_IS_NOT_SET) : token_type * token_type * address)
    | Some addr ->
    store.token_type_a, store.token_type_b, addr