let update_multisig (param : address) (store : storage) : return =
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateMultisig" sender_address : address contract option) with
          | None -> (failwith("no updateMultisig entrypoint") : operation list)
          | Some update_multisig_entrypoint ->
            [Tezos.transaction param 0mutez update_multisig_entrypoint]
        in
        (prepare_multisig "updateMultisig" param func store), store
    else
        ([] : operation list), { store with multisig = param }