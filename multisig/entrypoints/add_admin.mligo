let add_admin (param : address) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            let add_admin_entrypoint =
                Option.unopt (Tezos.get_entrypoint_opt "%addAdmin" sender_address : address contract option) in
            [Tezos.transaction param 0mutez add_admin_entrypoint] in
        (prepare_multisig "addAdmin" param func), store 
    else 
        ([] : operation list), { store with admins = Set.add param store.admins }