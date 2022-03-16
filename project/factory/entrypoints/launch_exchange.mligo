let launch_exchange(param : launch_exchange_params) (store : storage) : return =
    let sink_addr =
        match store.default_sink with
        | None -> (failwith error_SINK_CONTRACT_HAS_NOT_YET_DEPLOYED : address)
        | Some sink_addr -> sink_addr in
    let reserve_address = store.default_reserve in
    let token_a = param.token_type_a in
    let token_b = param.token_type_b in

    if check_tokens_equal token_a token_b then
        (failwith error_TOKENS_ARE_EQUAL : return)
    else if 
        Big_map.mem (token_a, token_b) store.pairs ||
        Big_map.mem (token_b, token_a) store.pairs then
        (failwith error_PAIR_ALREADY_EXISTS : return)
    else
        let token_amount_a = 
            match param.token_amount_a with
            | Mutez -> 
                if token_a = Xtz then
                    mutez_to_natural Tezos.amount
                else (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : nat)
            | Amount p ->
                if token_a <> Xtz then
                    p
                else
                    (failwith(error_XTZ_AMOUNT_SHOULD_BE_SENT) : nat)
            in
        let token_amount_b =
            match param.token_amount_b with
            | Mutez -> 
                if token_b = Xtz then
                    mutez_to_natural Tezos.amount
                else (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : nat)
            | Amount p -> 
                if token_b <> Xtz then
                    p
                else
                    (failwith(error_XTZ_AMOUNT_SHOULD_BE_SENT) : nat)
            in 
        if token_amount_a = 0n || token_amount_b = 0n then
            (failwith error_POOLS_CAN_NOT_BE_EMPTY : return)
        else
            if param.curve = Flat && token_amount_a <> token_amount_b then
                (failwith(error_FLAT_CURVE_EXCHANGE_SHOULD_HAVE_EQUAL_POOLS) : return)
            else
                let initial_lqt_total = sqrt (token_amount_a * token_amount_b) in

                let ops = ([] : operation list) in

                let dex_init_storage = 
                {
                    self_is_updating_token_pool = false;
                    token_pool_a = token_amount_a;
                    token_pool_b = token_amount_b;
                    token_type_a = param.token_type_a;
                    token_type_b = param.token_type_b;
                    token_type_smak = store.default_smak_token_type;
                    reserve = reserve_address;
                    lqt_address = (None : address option);
                    lqt_total = initial_lqt_total;
                    curve = param.curve;
                    manager = Tezos.self_address;
                    freeze_baker = false;
                    sink = sink_addr;
                    baker_rewards = (None : address option);
                    reward_rate = store.default_reward_rate;
                } in
                let (op_deploy_dex, dex_address) = deploy_dex dex_init_storage in

                let ops = op_deploy_dex :: ops in

                let lp_token_init_storage =
                    {
                        tokens = 
                            Big_map.update Tezos.sender (Some initial_lqt_total) (Big_map.empty : tokens);
                        allowances = store.default_lp_allowances;
                        admin = dex_address;
                        total_supply = initial_lqt_total;
                        token_metadata = store.default_lp_token_metadata;
                        metadata = store.default_lp_metadata;
                    } in

                let (op_deploy_lp_token, lp_token_address) =
                    deploy_lp_token lp_token_init_storage in

                let ops = op_deploy_lp_token :: ops in

                let rewards_provider_data =
                {
                    counter = 0n;
                    lqt_shares = initial_lqt_total;
                    accumulated = 0mutez;
                } in
                let rewards_history =
                    {
                        total_lqt = initial_lqt_total;
                        total_fees = 0mutez;
                    } in

                let baker_rewards_init_storage =
                    {
                        providers = (Big_map.literal [Tezos.sender, rewards_provider_data] : (address, baker_rewards_provider_data) big_map);
                        total_lp_tokens = initial_lqt_total;
                        dex_address = dex_address;
                        lqt_history = (Big_map.literal [0n, rewards_history] : (nat, baker_rewards_history) big_map);
                        counter = 0n;
                    } in

                let (op_deploy_baker_rewards, baker_rewards_address) = deploy_baker_rewards baker_rewards_init_storage in

                let ops =
                    if param.token_type_a = Xtz || param.token_type_b = Xtz then 
                        op_deploy_baker_rewards :: ops
                    else
                        ops in

                let new_store =
                    {
                      store with
                      pools =
                        (Big_map.update store.counter (Some dex_address) store.pools);
                      pairs =
                        (Big_map.update (token_a, token_b) (Some dex_address) store.pairs);
                      counter = (store.counter + 1n);
                    } in

                let ops =
                    match make_transfer_to_dex
                            token_a
                            Tezos.sender 
                            dex_address
                            token_amount_a
                    with
                    | None -> ops
                    | Some op -> op :: ops in

                let ops =
                    match make_transfer_to_dex
                            token_b
                            Tezos.sender 
                            dex_address
                            token_amount_b
                    with
                    | None -> ops
                    | Some op -> op :: ops in

                let set_lqt_address_entrypoint : set_lqt_address_params contract =
                    match (Tezos.get_entrypoint_opt "%setLqtAddress" Tezos.self_address : 
                             set_lqt_address_params contract option)
                    with
                    | None ->
                      (failwith error_SELF_SET_LQT_ADDRESS_DOES_NOT_EXIST : set_lqt_address_params
                           contract)
                    | Some contract -> contract in

                let set_lqt_address =
                    Tezos.transaction
                        { dex_address = dex_address ; lqt_address = lp_token_address }
                        0mutez set_lqt_address_entrypoint in

                let ops = set_lqt_address :: ops in

                let set_baker =
                    match (Tezos.get_entrypoint_opt "%setBaker" Tezos.self_address : set_baker_param contract option) with
                    | None -> (failwith(error_SELF_SET_BAKER_ENTRYPOINT) : set_baker_param contract)
                    | Some contr -> contr in

                let (freeze_baker, baker) =
                    match (token_a, token_b) with
                    | (Xtz, _) -> (false, (Some store.default_baker))
                    | (_, Xtz) -> (false, (Some store.default_baker))
                    | _ -> (true, (None : key_hash option))
                    in

                let set_baker_param =
                    {
                        dex_address = dex_address;
                        baker = baker;
                        freeze_baker = freeze_baker;
                    } in

                let op_set_baker = Tezos.transaction set_baker_param 0mutez set_baker in

                let ops = op_set_baker :: ops in

                let set_rewards_address_entrypoint : set_rewards_address_param contract =
                    match (Tezos.get_entrypoint_opt "%setRewardsAddress" Tezos.self_address : 
                             set_rewards_address_param contract option)
                    with
                    | None ->
                      (failwith error_SELF_SET_REWARDS_ADDRESS_DOES_NOT_EXIST : set_rewards_address_param
                           contract)
                    | Some contract -> contract in

                let op_set_rewards_address =
                    Tezos.transaction
                        { dex_address = dex_address ; rewards_address = baker_rewards_address }
                        0mutez set_rewards_address_entrypoint in

                let ops = op_set_rewards_address :: ops in

                let sink_add_exchange =
                    match (Tezos.get_entrypoint_opt "%addExchange" sink_addr : sink_add_exchange_param contract option) with
                    | None -> (failwith(error_NO_SINK_ADD_EXCHANGE) : sink_add_exchange_param contract)
                    | Some contr -> contr in
                let sink_add_exchange_param =
                    {
                        dex_address = dex_address; 
                        token_a = token_a;
                        token_b = token_b;
                    } in

                let op_sink_add_exchange =
                    Tezos.transaction sink_add_exchange_param 0mutez sink_add_exchange in

                let ops = op_sink_add_exchange :: ops in

                let reversed_ops = ([] : operation list) in

                let reversed_ops = List.fold (fun (ops, op : operation list * operation) -> op :: ops) ops reversed_ops in

                reversed_ops, new_store

                    