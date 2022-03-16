let launch_sink (store : storage) : return =
  if Tezos.sender <> store.admin then
    (failwith(error_ONLY_ADMIN_CAN_LAUNCH_SINK) : return)
  else
    match store.default_sink with
    | Some _ -> (failwith error_SINK_CONTRAT_HAS_ALREADY_BEEN_DEPLOYED : return)
    | None ->
      let init_store_sink : sink_storage =
        {
          token_type_smak = store.default_smak_token_type;
          factory_address = Tezos.self_address;
          burn = (Big_map.empty : (token_type, nat) big_map);
          reserve = (Big_map.empty : (token_type, nat) big_map);
          reserve_address = store.default_reserve;
          token_claim_limit = store.default_claim_limit;
          exchanges = store.pairs;
        } in
      let (op, sink_address) = deploy_sink init_store_sink in
      let new_store = { store with default_sink = (Some sink_address) } in
      [op], new_store