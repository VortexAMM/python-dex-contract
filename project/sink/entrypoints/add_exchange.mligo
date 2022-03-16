let add_exchange (param : add_exchange_param) (store : storage) : return =
    if Tezos.sender <> store.factory_address then
        (failwith(error_ONLY_FACTORY_CAN_ADD_EXCHANGE) : return)
    else
        let {token_a; token_b; dex_address} = param in
        let new_exchanges =
            Big_map.update (token_a, token_b) (Some dex_address) store.exchanges in
        let new_store = { store with exchanges = new_exchanges } in
        let ops = ([] : operation list) in
        let ops =
            match token_a with
            | Fa2 (fa2_addr, token_id) ->
                let approve =
                    [Add_operator
                       {
                         owner = Tezos.self_address;
                         operator = dex_address;
                         token_id = token_id;
                       }] in
                    (external_update_operators_fa2 fa2_addr approve) :: ops
            | _ -> ops in
        let ops =
            match token_b with
            | Fa2 (fa2_addr, token_id) ->
                let approve =
                    [Add_operator
                       {
                         owner = Tezos.self_address;
                         operator = dex_address;
                         token_id = token_id;
                       }] in
                    (external_update_operators_fa2 fa2_addr approve) :: ops
            | _ -> ops in

        ops, new_store
        
