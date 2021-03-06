let remove_exchange (param : remove_exchange_param) (store : storage) : return =
    let () = no_xtz in
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        let remove_exchange_entrypoint =
            Option.unopt (Tezos.get_entrypoint_opt "%removeExchange" sender_address : remove_exchange_param contract option) in
        [Tezos.transaction param 0mutez remove_exchange_entrypoint] in
        (prepare_multisig "removeExchange" param func store), store
    else
        let {token_a; token_b; index} = param in
        let (pairs, dex_address, tokens) =
            match Big_map.find_opt (token_a, token_b) store.pairs with
            | Some dex_addr ->
                (Big_map.update (token_a, token_b) (None : address option) store.pairs, dex_addr, (token_a, token_b))
            | None ->
                let reverse_dex =
                    match Big_map.find_opt (token_b, token_a) store.pairs with
                    | None ->
                        (failwith(error_EXCHANGE_NOT_IN_PAIRS) : address) // 136
                    | Some rev_addr -> rev_addr in
                (Big_map.update (token_b, token_a) (None : address option) store.pairs, reverse_dex, (token_b, token_a)) in
        let pools =
            match Big_map.find_opt index store.pools with
            | None ->
                (failwith(error_EXCHANGE_NOT_IN_POOLS) : (nat, address) big_map) // 137
            | Some addr ->
                if addr <> dex_address then
                    (failwith(error_INDEX_NOT_MATCHING_TOKENS) : (nat, address) big_map) // 138
                else
                    Big_map.update index (None : address option) store.pools in
        let sink =
            match store.default_sink with
            | None -> (failwith(error_SINK_CONTRACT_HAS_NOT_YET_DEPLOYED) : address) // 104
            | Some addr -> addr in
        let sink_remove_exchange =
            match (Tezos.get_entrypoint_opt "%removeExchange" sink : sink_remove_exchange_param contract option) with
            | None -> (failwith(error_SINK_HAS_NO_REMOVE_EXCHANGE) : sink_remove_exchange_param contract) // 139
            | Some contr -> contr in
        let sink_remove_exchange_param =
        {
            token_a = tokens.0;
            token_b = tokens.1;
            dex_address = dex_address;
        } in
        let ops = [Tezos.transaction sink_remove_exchange_param 0mutez sink_remove_exchange] in
        let new_store = { store with pairs = pairs; pools = pools } in
        ops, new_store