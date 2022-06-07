let rec update_baker_rec (counter : nat) (last : nat) (baker_address : key_hash) (operations : operation list) (store : storage) : operation list =
    if counter = last then
        operations
    else
        let dex_address =
            match Big_map.find_opt counter store.pools with
            | None -> (failwith(error_EXCHANGE_NOT_IN_POOLS) : address)
            | Some addr -> addr in
        let set_baker_contr =
            Option.unopt ((Tezos.get_entrypoint_opt "%setBaker" dex_address) : dex_set_baker_param contract option) in
        let set_baker_param =
        {
            baker = Some baker_address;
            freeze_baker = false;
        } in
        let ops = Tezos.transaction set_baker_param 0mutez set_baker_contr :: operations in
        let counter = counter + 1n in

        update_baker_rec counter last baker_address ops store

let update_baker (param : update_baker_param) (store : storage) : return =
    let () = no_xtz in
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        let update_baker_entrypoint =
            Option.unopt (Tezos.get_entrypoint_opt "%updateBaker" sender_address : update_baker_param contract option) in
        [Tezos.transaction param 0mutez update_baker_entrypoint] in
        (prepare_multisig "updateBaker" param func store), store
    else
        let { baker; first_pool; number_of_pools } = param in
        if first_pool > store.counter then
            (failwith(error_FIRST_POOL_TO_UPDATE_IS_OUT_OF_RANGE) : return)
        else
            let last_pool =
                if first_pool + number_of_pools > store.counter then
                    store.counter
                else
                    first_pool + number_of_pools in
            let ops = ([] : operation list) in
            let ops = update_baker_rec first_pool last_pool baker ops store in
            let new_store = { store with default_baker = baker } in
            ops, new_store