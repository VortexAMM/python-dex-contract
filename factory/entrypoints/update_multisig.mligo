let update_multisig (param : address) (store : storage) : return =
    let () = no_xtz in
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        let update_multisig_entrypoint =
          Option.unopt (Tezos.get_entrypoint_opt "%updateMultisig" sender_address : address contract option) in
        [Tezos.transaction param 0mutez update_multisig_entrypoint] in
        (prepare_multisig "updateMultisig" param func store), store
    else
        ([] : operation list), { store with multisig = param }