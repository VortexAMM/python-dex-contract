let launch_sink (store : storage) : return =
  let () = no_xtz in
  if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        let launch_sink_entrypoint = 
          Option.unopt (Tezos.get_entrypoint_opt "%launchSink" sender_address : unit contract option) in
            [Tezos.transaction () 0mutez launch_sink_entrypoint]
        in
        (prepare_multisig "launchSink" () func store), store
  else
    match store.default_sink with
    | Some _ -> (failwith error_SINK_CONTRAT_HAS_ALREADY_BEEN_DEPLOYED : return) // 112
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