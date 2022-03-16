let set_sink_claim_limit (param : nat) (store : storage) : return =
    if Tezos.sender <> store.admin then
        (failwith(error_ONLY_ADMIN_CAN_SET_CLAIM_LIMIT) : return)
    else
        let sink_address =
            match store.default_sink with
            | None -> (failwith(error_SINK_CONTRACT_HAS_NOT_YET_DEPLOYED) : address)
            | Some addr -> addr in
        let sink_set_claim_limit = 
            match (Tezos.get_entrypoint_opt "%updateClaimLimit" sink_address : nat contract option) with
            | None -> (failwith(error_SINK_HAS_NO_UPDATE_CLAIM_LIMIT) : nat contract)
            | Some contr -> contr in
        let op = Tezos.transaction param 0mutez sink_set_claim_limit in
    [op], { store with default_claim_limit = param }