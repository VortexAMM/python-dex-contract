let launch_sink (store : storage) =
  match store.default_reserve with
  | Some _ -> (failwith error_SINK_CONTRAT_HAS_ALREADY_BEEN_DEPLOYED : return)
  | None ->
    let init_store_sink : sink_storage =
      {
        token_smak = store.default_token_smak;
        fa_token_smak = store.default_smak_token_type;
        factory_address = Tezos.self_address
      } in
    let (op, sink_address) = deploy_sink init_store_sink in
    let new_store = { store with default_reserve = (Some sink_address) } in
    (([op], new_store) : return)