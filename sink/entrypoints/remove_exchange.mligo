let remove_exchange (param : remove_exchange_param) (store : storage) : return =
    if Tezos.sender <> store.factory_address then
        (failwith(error_ONLY_FACTORY_CAN_REMOVE_EXCHANGE) : return)
    else
        let {token_a; token_b; dex_address} = param in
            match Big_map.find_opt (token_a, token_b) store.exchanges with
            | None -> (failwith(error_EXCHANGE_NOT_LISTED) : return)
            | Some addr -> 
                if addr <> dex_address then
                    (failwith(error_ADDRESS_SUPPLIED_BY_FACTORY_NOT_IN_STORAGE) : return)
                else
                    let exchanges =
                        Big_map.update (token_a, token_b) (None : address option) store.exchanges in
                    ([] : operation list), { store with exchanges = exchanges }
