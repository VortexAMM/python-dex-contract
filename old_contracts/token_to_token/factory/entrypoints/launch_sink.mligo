#if !FACTORY_LAUNCH_SINK
#define FACTORY_LAUNCH_SINK

let launch_sink (storage : storage) =
  match storage.default_reserve with
  | Some _ -> (failwith error_SINK_CONTRAT_HAS_ALREADY_BEEN_DEPLOYED : result)
  | None ->
    let init_storage_sink : sink_storage =
      {
        token_smak = storage.default_token_smak;
        fa_token_smak = storage.default_smak_fa_token;
        factory_address = Tezos.self_address
      } in
    let (op, sink_address) = deploy_sink init_storage_sink in
    let new_storage = { storage with default_reserve = (Some sink_address) } in
    (([op], new_storage) : result)

#endif