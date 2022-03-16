let set_rewards_address (param : set_rewards_address_param) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        (failwith error_ONLY_SELF_CAN_SET_REWARDS_ADDRESS : return)
    else
        let set_rewards_address_entrypoint : address contract =
            match (Tezos.get_entrypoint_opt "%setRewardsAddress" param.dex_address : address contract option) with
            | None -> (failwith error_DEX_SET_REWARDS_ADDRESS_DOES_NOT_EXIST : address contract)
            | Some contract -> contract in
        let set_rewards_address =
            Tezos.transaction param.rewards_address 0mutez set_rewards_address_entrypoint in
        ([set_rewards_address], store)