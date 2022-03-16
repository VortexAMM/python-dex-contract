#if !DEX_UPDATE_TOKEN_POOL_INTERNAL
#define DEX_UPDATE_TOKEN_POOL_INTERNAL

let update_token_pool_internal (token_pool : update_token_pool_internal) (storage : storage) : result =
  let storage =
    match token_pool with
    | FA2InternalA token_pool ->
      let () =
        update_token_pool_internal_checks storage.token_address_a storage in
      { storage with token_pool_a = (fa2_balance_callback token_pool) }
    | FA12InternalA token_pool ->
      let () =
        update_token_pool_internal_checks storage.token_address_a storage in
      { storage with token_pool_a = token_pool }
    | FA2InternalB token_pool ->
      let () =
        update_token_pool_internal_checks storage.token_address_b storage in
      { storage with token_pool_b = (fa2_balance_callback token_pool) }
    | FA12InternalB token_pool ->
      let () =
        update_token_pool_internal_checks storage.token_address_b storage in
      { storage with token_pool_b = token_pool }
    | UpdateTokenEnded -> { storage with self_is_updating_token_pool = false } in
  (([] : operation list), storage)

#endif