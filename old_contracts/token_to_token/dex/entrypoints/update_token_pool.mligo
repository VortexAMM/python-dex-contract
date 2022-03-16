#if !DEX_UPDATE_TOKEN_POOL
#define DEX_UPDATE_TOKEN_POOL

let update_token_pool (storage : storage) : result =
  let () = check_sender Tezos.source in
  let () = check_self_is_not_updating_token_pool storage in
  let opA =
    update_token_pool_aux storage.token_id_a storage.token_address_a
      get_entrypoint_A2 get_entrypoint_A12 in
  let opB =
    update_token_pool_aux storage.token_id_b storage.token_address_b
      get_entrypoint_B2 get_entrypoint_B12 in
  let update_ended = update_ended_callback () in
  let storage = { storage with self_is_updating_token_pool = true } in
  (([opA; opB; update_ended] : operation list), storage)

#endif