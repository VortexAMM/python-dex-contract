let rec updates (counter : nat) (last : nat) (sink_address : address) (operations : operation list) (store : storage) : operation list =
    if counter = last then
        operations
    else
        let current_exchange = 
            match Big_map.find_opt counter store.pools with
            | None -> (failwith(error_COUNTER_OUTSIDE_POOL_LIMIT) : address)
            | Some addr -> addr in
        let update_sink_contr =
            match (Tezos.get_entrypoint_opt "%updateSinkAddress" current_exchange : address contract option) with
            | None -> (failwith(error_EXCHANGE_HAS_NO_UPDATE_SINK_ENTRYPOINT) : address contract)
            | Some contr -> contr in
        let ops = Tezos.transaction sink_address 0mutez update_sink_contr :: operations in
        let new_counter = counter + 1n in
        updates new_counter last sink_address ops store
        

let update_sink_address (param : update_sink_address_param) (store : storage) : return =
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateSinkAddress" sender_address : update_sink_address_param contract option) with
          | None -> (failwith("no updateSinkAddress entrypoint") : operation list)
          | Some update_sink_address_entrypoint ->
            [Tezos.transaction param 0mutez update_sink_address_entrypoint]
        in
        (prepare_multisig "updateSinkAddress" param func store), store
    else
        let ops = ([] : operation list) in
        let {
            number_of_pools;
            first_pool;
            new_sink_address;
        } = param in
        if first_pool + number_of_pools > store.counter then
            (failwith(error_COUNTER_OUTSIDE_POOL_LIMIT) : return)
        else
            let ops = updates first_pool (first_pool + number_of_pools) new_sink_address ops store in
            (ops), { store with default_sink = (Some new_sink_address) }