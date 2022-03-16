#if !FACTORY_LAUNCH_EXCHANGE
#define FACTORY_LAUNCH_EXCHANGE

let launch_exchange (launch_exchange_param : launch_exchange_param) (storage : storage) : result =
  let sink_addr =
    match storage.default_reserve with
    | None -> (failwith error_SINK_CONTRACT_HAS_NOT_YET_DEPLOYED : address)
    | Some sink_addr -> sink_addr in
  let token_a = (launch_exchange_param.address_a, launch_exchange_param.id_a) in
  let token_b = (launch_exchange_param.address_b, launch_exchange_param.id_b) in
  if check_tokens_are_equal token_a token_b
  then (failwith error_CANNOT_CREATE_TOKEN_WITH_SAME_ADDRESS : result)
  else
  if
    (Big_map.mem (token_a, token_b) storage.pairs) ||
    (Big_map.mem (token_b, token_a) storage.pairs)
  then (failwith error_TOKEN_ALREADY_EXISTS : result)
  else
  if
    (launch_exchange_param.amount_a = 0n) ||
    (launch_exchange_param.amount_b = 0n)
  then (failwith error_INITIAL_VALUE_OF_POOL_CANNOT_BE_ZERO : result)
  else
    (let last_k =
       launch_exchange_param.amount_a * launch_exchange_param.amount_b in
     let initial_lqt_total : nat = sqrt last_k in
     let initial_swaps_history =
       let initial_swaps_history_pool_a =
         Big_map.update "token_pool_a"
           (Some launch_exchange_param.amount_a)
           (Big_map.empty : (string, nat) big_map) in
       Big_map.update "token_pool_b" (Some launch_exchange_param.amount_b)
         initial_swaps_history_pool_a in
     let initial_user_investments =
       Big_map.update Tezos.sender
         (Some
            {
              token_invest_a = launch_exchange_param.amount_a;
              token_invest_b = launch_exchange_param.amount_b;
              direction = ADD
            }) (Big_map.empty : (address, investment_delta) big_map) in
     let dex_init_storage : dex_storage =
       {
         token_pool_a = launch_exchange_param.amount_a;
         token_pool_b = launch_exchange_param.amount_b;
         lqt_total = initial_lqt_total;
         self_is_updating_token_pool = false;
         manager = Tezos.self_address;
         token_address_a = launch_exchange_param.address_a;
         token_address_b = launch_exchange_param.address_b;
         token_address_smak = storage.default_token_smak;
         token_id_a = launch_exchange_param.id_a;
         token_id_b = launch_exchange_param.id_b;
         token_id_smak = storage.default_smak_fa_token;
         lqt_address = (None : address option);
         history = initial_swaps_history;
         user_investments = initial_user_investments;
         reserve = sink_addr;
         last_k = last_k;
         curve = launch_exchange_param.curve;
       } in
     let (op_deploy_dex, dex_address) = deploy_dex dex_init_storage in
     let lp_token_init_storage =
       {
         tokens =
           (Big_map.update Tezos.sender (Some initial_lqt_total)
              (Big_map.empty : tokens));
         allowances = storage.default_lp_allowances;
         admin = dex_address;
         total_supply = initial_lqt_total;
         token_metadata = storage.default_lp_token_metadata;
         metadata = storage.default_lp_metadata
       } in
     let (op_deploy_lp_token, lp_token_address) =
       deploy_lp_token lp_token_init_storage in
     let new_storage =
       {
         storage with
         pools =
           (Big_map.update storage.counter (Some dex_address) storage.pools);
         pairs =
           (Big_map.update (token_a, token_b) (Some dex_address)
              storage.pairs);
         counter = (storage.counter + 1n)
       } in
     let op_tokens_a_transfer : operation =
       match make_fa_transfer launch_exchange_param.id_a
               launch_exchange_param.address_a Tezos.sender dex_address
               launch_exchange_param.amount_a
       with
       | None ->
         (failwith error_INITIAL_VALUE_OF_POOL_CANNOT_BE_ZERO : operation)
       | Some op -> op in
     let op_tokens_b_transfer =
       match make_fa_transfer launch_exchange_param.id_b
               launch_exchange_param.address_b Tezos.sender dex_address
               launch_exchange_param.amount_b
       with
       | None ->
         (failwith error_INITIAL_VALUE_OF_POOL_CANNOT_BE_ZERO : operation)
       | Some op -> op in
     let set_lqt_address_entrypoint : set_lqt_address_param contract =
       match (Tezos.get_entrypoint_opt "%setLqtAddress" Tezos.self_address : 
                set_lqt_address_param contract option)
       with
       | None ->
         (failwith error_SELF_SET_LQT_ADDRESS_DOES_NOT_EXIST : set_lqt_address_param
              contract)
       | Some contract -> contract in
     let set_lqt_address =
       Tezos.transaction
         { dex_address = dex_address ; lqt_address = lp_token_address }
         0mutez set_lqt_address_entrypoint in
     (([op_deploy_dex;
        op_deploy_lp_token;
        op_tokens_a_transfer;
        op_tokens_b_transfer;
        set_lqt_address], new_storage) : result))

#endif