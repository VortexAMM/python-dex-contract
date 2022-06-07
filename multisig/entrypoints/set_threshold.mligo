let set_threshold (param : nat) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            let set_threshold_entrypoint =
                Option.unopt (Tezos.get_entrypoint_opt "%setThreshold" sender_address : nat contract option) in
            [Tezos.transaction param 0mutez set_threshold_entrypoint] in
        (prepare_multisig "setThreshold" param func), store 
    else if param = 0n then
        (failwith(error_THRESHOLD_CAN_NOT_BE_ZERO) : return)
    else if param > Set.cardinal store.admins then
        (failwith(error_THRESHOLD_TOO_HIGH) : return)
    else
        ([] : operation list), { store with threshold = param }