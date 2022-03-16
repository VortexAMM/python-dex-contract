let launch_exchange(param : launch_exchange_params) (store : storage) : return =
    let sink_addr =
    match store.default_reserve with
    | None -> (failwith error_SINK_CONTRACT_HAS_NOT_YET_DEPLOYED : address)
    | Some sink_addr -> sink_addr in
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
            | Mutez -> mutez_to_natural Tezos.amount
            | Amount p -> p in 
        let token_amount_b =
            match param.token_amount_b with
            | Mutez -> mutez_to_natural Tezos.amount
            | Amount p -> p in 
        if token_amount_a = 0n || token_amount_b = 0n then
            (failwith error_POOLS_CAN_NOT_BE_EMPTY : return)
        else
            let last_k = token_amount_a * token_amount_b in
            let initial_lqt_total = sqrt last_k in

            let initial_swaps_history = 
                let initial_swaps_history_pool_a =
                    Big_map.update
                        "token_pool_a"
                        (Some token_amount_a)
                        (Big_map.empty : ((string, nat) big_map)) in
                Big_map.update
                    "token_pool_b"
                    (Some token_amount_b)
                    initial_swaps_history_pool_a in

            let initial_user_investments =
                Big_map.update
                    Tezos.sender
                    (
                        Some
                        {
                            token_invest_a = token_amount_a;
                            token_invest_b = token_amount_b;
                            direction = Add;
                        }
                    ) 
                    (Big_map.empty : ((address, user_investment) big_map)) in

            let dex_init_storage = 
            {
                self_is_updating_token_pool = false;
                token_pool_a = token_amount_a;
                token_pool_b = token_amount_b;
                token_type_a = param.token_type_a;
                token_type_b = param.token_type_b;
                token_type_smak = store.default_smak_token_type;
                reserve = sink_addr;
                lqt_total = initial_lqt_total;
                history = initial_swaps_history;
                user_investments = initial_user_investments;
                lqt_address = (None : address option);
                last_k = last_k;
                curve = param.curve;
                manager = Tezos.self_address;
                freeze_baker = false;
            } in
            let (op_deploy_dex, dex_address) = deploy_dex dex_init_storage in
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
            
            let new_store =
                {
                  store with
                  pools =
                    (Big_map.update store.counter (Some dex_address) store.pools);
                  pairs =
                    (Big_map.update (token_a, token_b) (Some dex_address)
                       store.pairs);
                  counter = (store.counter + 1n)
                } in

            let op_tokens_a_transfer : operation =
                match make_transfer 
                        token_a
                        Tezos.sender 
                        dex_address
                        token_amount_a
                with
                | None ->
                  (failwith error_INITIAL_VALUE_OF_POOL_CANNOT_BE_ZERO : operation)
                | Some op -> op in

            let op_tokens_b_transfer : operation =
                match make_transfer 
                        token_b
                        Tezos.sender 
                        dex_address
                        token_amount_b
                with
                | None ->
                  (failwith error_INITIAL_VALUE_OF_POOL_CANNOT_BE_ZERO : operation)
                | Some op -> op in

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
            [op_deploy_dex;
            op_deploy_lp_token;
            op_tokens_a_transfer;
            op_tokens_b_transfer;
            set_lqt_address], new_store

            (* 
                TODO: deploy sink
                TODO: inner set_baker
             *)
                    