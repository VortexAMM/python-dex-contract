[@view] let get_dex_address (param, store : get_dex_address_param * storage) : address * bool =
    match Big_map.find_opt (param.a_type, param.b_type) store.pairs with
    | Some addr -> addr, true
    | None ->
        let reverse_pair = 
            match Big_map.find_opt (param.b_type, param.a_type) store.pairs with
            | None -> (failwith(error_PAIR_DOES_NOT_EXIST_FACTORY) : address * bool)
            | Some addr -> addr, false in
            reverse_pair