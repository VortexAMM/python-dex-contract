let set_baker (param : set_baker_param) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        (failwith(error_ONLY_SELF_CAN_SET_BAKER) : return) // 119
    else
        let dex_set_baker =
            match (Tezos.get_entrypoint_opt "%setBaker" param.dex_address : dex_set_baker_param contract option) with
            | None -> (failwith(error_DEX_HAS_NO_SET_BAKER_ENTRYPOINT) : dex_set_baker_param contract) // 120
            | Some contr -> contr in
        let baker_params = {
            freeze_baker = param.freeze_baker;
            baker = param.baker;
        } in
        [Tezos.transaction baker_params 0mutez dex_set_baker], store