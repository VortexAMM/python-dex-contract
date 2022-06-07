let remove_admin (param : address) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%removeAdmin" sender_address : address contract option) with
            | None -> (failwith("no removeAdmin entrypoint") : operation list)
            | Some remove_admin_entrypoint -> [Tezos.transaction param 0mutez remove_admin_entrypoint] in
        (prepare_multisig "removeAdmin" param func), store 
    else if Set.cardinal store.admins = 1n then
        (failwith(error_ADMIN_SET_CANNOT_BE_EMPTY) : return)
    else if Set.cardinal store.admins = store.threshold then
        (failwith(error_ADMIN_SET_MUST_BE_LARGER_THAN_THRESHOLD) : return)
    else
        ([] : operation list), { store with admins = Set.remove param store.admins }