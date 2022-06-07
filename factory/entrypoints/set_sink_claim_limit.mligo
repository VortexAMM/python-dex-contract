let set_sink_claim_limit (param : nat) (store : storage) : return =
    let () = no_xtz in
    if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        let set_claim_limit_entrypoint =
            Option.unopt (Tezos.get_entrypoint_opt "%setSinkClaimLimit" sender_address : nat contract option) in
        [Tezos.transaction param 0mutez set_claim_limit_entrypoint] in
        (prepare_multisig "setSinkClaimLimit" param func store), store
    else
        let sink_address =
            match store.default_sink with
            | None -> (failwith(error_SINK_CONTRACT_HAS_NOT_YET_DEPLOYED) : address) // 104
            | Some addr -> addr in
        let sink_set_claim_limit = 
            match (Tezos.get_entrypoint_opt "%updateClaimLimit" sink_address : nat contract option) with
            | None -> (failwith(error_SINK_HAS_NO_UPDATE_CLAIM_LIMIT) : nat contract) // 126 UNREACHABLE
            | Some contr -> contr in
        let op = Tezos.transaction param 0mutez sink_set_claim_limit in
    [op], { store with default_claim_limit = param }