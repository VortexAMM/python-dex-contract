let add_authorized_contract (param : address) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            let add_authorized_contract_entrypoint = 
                Option.unopt (Tezos.get_entrypoint_opt "%addAuthorizedContract" sender_address : address contract option) in
            [Tezos.transaction param 0mutez add_authorized_contract_entrypoint] in
        (prepare_multisig "addAuthorizedContract" param func), store 
    else
        let new_authorized_contract = Set.add param store.authorized_contracts in
        ([] : operation list), { store with authorized_contracts = new_authorized_contract }