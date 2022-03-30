let rec one_baker_update (counter : nat) (last : nat) (baker_address : key_hash) (operations : operation list) (store : storage) : operation list =
    if counter = last then
        operations
    else
        let dex_address =
            match Big_map.find_opt counter store.pools with
            | None -> (failwith("no pool") : address)
            | Some addr -> addr in
        let set_baker_contr =
            match (Tezos.get_entrypoint_opt "%setBaker" dex_address : dex_set_baker_param contract option) with
            | None -> (failwith("no setBaker entrypoint") : dex_set_baker_param contract)
            | Some contr -> contr in
        let set_baker =
        {
            baker = Some baker_address;
            freeze_baker = false;
        } in
        let ops = Tezos.transaction set_baker 0mutez set_baker_contr :: operations in
        let counter = counter + 1n in

        one_baker_update counter last baker_address ops store

let update_baker (param : update_baker_param) (store : storage) : return =
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateBaker" sender_address : update_baker_param contract option) with
          | None -> (failwith("no updateBaker entrypoint") : operation list)
          | Some update_baker_entrypoint ->
            [Tezos.transaction param 0mutez update_baker_entrypoint]
        in
        (prepare_multisig "updateBaker" param func store), store
    else
        let { baker; first_pool; number_of_pools } = param in
        let last_pool =
        if first_pool + number_of_pools > store.counter then
            store.counter
        else
            first_pool + number_of_pools in
        let ops = ([] : operation list) in
        let ops = one_baker_update first_pool last_pool baker ops store in
        let new_store = { store with default_baker = baker } in
        ops, new_store