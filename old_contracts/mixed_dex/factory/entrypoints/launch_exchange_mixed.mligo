#if !FACTORY_LAUNCH_EXCHANGE_MIXED
#define FACTORY_LAUNCH_EXCHANGE_MIXED

let launch_exchange_mixed (self: address) (launch_exchange_param: launch_exchange_param) (s: storage)  =
#if FA2
    if Big_map.mem (launch_exchange_param.token_address, launch_exchange_param.token_id) s.token_to_swaps then
#else
    if Big_map.mem launch_exchange_param.token_address s.token_to_swaps then
#endif
        (failwith error_TOKEN_ALREADY_EXISTS : result)
    else
        let lqt_total = mutez_to_natural Tezos.amount in
        let history = Big_map.update "token_pool" (Some (launch_exchange_param.token_amount)) s.empty_history in
        let history = Big_map.update "xtz_pool" (Some (mutez_to_natural Tezos.amount)) history in
        let history = Big_map.update "xtz_volume" (Some 0n) history in
        let user_investments = Big_map.update Tezos.sender (Some {xtz=Tezos.amount; token=launch_exchange_param.token_amount; direction=Add}) s.empty_user_investments in
        let dex_init_storage : dex_storage = {
          token_pool = launch_exchange_param.token_amount;
          xtz_pool = Tezos.amount ;
          lqt_total = lqt_total ;
          self_is_updating_token_pool = false ;
          freeze_baker = false ;
          multisig = ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address);
          manager = self ;
          token_address = launch_exchange_param.token_address ;
#if FA2
          token_id = launch_exchange_param.token_id;
#endif
          lqt_address = ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address) ;
          history = history ;
          user_investments = user_investments ;
          reserve = s.default_reserve ;
        } in

        let dex_res = deploy_dex (dex_init_storage) in

        //let lp_token_metadata = Big_map.update "swap" (Some (Bytes.pack launch_exchange_param.token_address)) s.default_metadata in
        let lp_token_init_storage = {
            tokens = Big_map.update Tezos.sender (Some lqt_total) s.empty_tokens;
            allowances = s.empty_allowances;
            admin = dex_res.1;
            total_supply = lqt_total;
            token_metadata = s.default_token_metadata;
            metadata = s.default_metadata;
        } in

        let lp_token_res = deploy_lp_token (lp_token_init_storage) in

        let new_storage = {
          swaps = Big_map.update s.counter (Some dex_res.1) s.swaps;
#if FA2
          token_to_swaps = Big_map.update (launch_exchange_param.token_address, launch_exchange_param.token_id)  (Some dex_res.1) s.token_to_swaps;
#else
          token_to_swaps = Big_map.update launch_exchange_param.token_address  (Some dex_res.1) s.token_to_swaps;
#endif
          counter = s.counter + 1n;
          empty_tokens = s.empty_tokens;
          empty_allowances = s.empty_allowances;
          empty_history = s.empty_history;
          empty_user_investments = s.empty_user_investments;
          default_reserve = s.default_reserve;
          default_metadata = s.default_metadata;
          default_token_metadata = s.default_token_metadata;
        } in

#if FA2
        let transfer : transfer_fa2 contract =
        match (Tezos.get_entrypoint_opt "%transfer" launch_exchange_param.token_address :  transfer_fa2 contract option) with
        | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : transfer_fa2 contract)
        | Some contract -> contract in
        let transfer_param = [{
            from_ = Tezos.sender ;
            txs = [{
                to_ = dex_res.1;
                token_id = launch_exchange_param.token_id;
                amount = launch_exchange_param.token_amount
            }]
        }] in
        let transfer_tokens = Tezos.transaction transfer_param 0mutez transfer in
#else
        let transfer : transfer contract =
        match (Tezos.get_entrypoint_opt "%transfer" launch_exchange_param.token_address :  transfer contract option) with
        | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : transfer contract)
        | Some contract -> contract in
        let transfer_tokens = Tezos.transaction { address_from = Tezos.sender; address_to = dex_res.1; value = launch_exchange_param.token_amount } 0mutez transfer in
#endif

        let set_lqt_address_entrypoint : set_lqt_address_param contract =
        match (Tezos.get_entrypoint_opt "%setLqtAddress" self :  set_lqt_address_param contract option) with
        | None -> (failwith error_SELF_SET_LQT_ADDRESS_DOES_NOT_EXIST: set_lqt_address_param contract)
        | Some contract -> contract in
        let set_lqt_address = Tezos.transaction { dex_address = dex_res.1 ; lqt_address = lp_token_res.1 } 0mutez set_lqt_address_entrypoint in

        ([dex_res.0; lp_token_res.0; transfer_tokens; set_lqt_address], new_storage)

#endif