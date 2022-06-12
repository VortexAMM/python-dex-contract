let set_lqt_address(param : set_lqt_address_params) (store : storage) : return =
    let () = no_xtz in
    if Tezos.sender <> Tezos.self_address then
        (failwith error_ONLY_SELF_CAN_SET_LQT_ADDRESS : return) // 109
    else
        let set_lqt_address_entrypoint : address contract =
        match (Tezos.get_entrypoint_opt "%setLqtAddress" param.dex_address : address contract option) with
        | None ->
          (failwith error_DEX_SET_LQT_ADDRESS_DOES_NOT_EXIST : address contract) // 110
        | Some contract -> contract in
        let set_lqt_address =
        Tezos.transaction param.lqt_address 0mutez set_lqt_address_entrypoint in
        ([set_lqt_address], store)