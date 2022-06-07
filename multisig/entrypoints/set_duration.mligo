let set_duration (param : nat) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            let set_duration_entrypoint =
                Option.unopt (Tezos.get_entrypoint_opt "%setDuration" sender_address : nat contract option) in
            [Tezos.transaction param 0mutez set_duration_entrypoint] in
      (prepare_multisig "setDuration" param func), store 
    else if param = 0n then
        (failwith(error_DURATION_CANNOT_BE_ZERO) : return)
    else
        ([] : operation list), { store with duration = int param }