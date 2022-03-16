#if !DEX_UPDATE_TOKEN_POOL_INTERNAL
#define DEX_UPDATE_TOKEN_POOL_INTERNAL

let update_token_pool_internal (token_pool : update_token_pool_internal) (store : storage) : return =
    let token_address_a =
        match store.token_type_a with
        | Fa12 token_address -> token_address
        | Fa2 (token_address, _) -> token_address
        | Xtz -> (failwith "no address" : address) in
    let token_address_b =
        match store.token_type_b with
        | Fa12 token_address -> token_address
        | Fa2 (token_address, _) -> token_address
        | Xtz -> (failwith "no adderess" : address) in
  let new_store =
    match token_pool with
    | FA2InternalA token_pool ->
      let () =
        update_token_pool_internal_checks token_address_a store in
      { store with token_pool_a = (fa2_balance_callback token_pool) }
    | FA12InternalA token_pool ->
      let () =
        update_token_pool_internal_checks token_address_a store in
      { store with token_pool_a = token_pool }
    | FA2InternalB token_pool ->
      let () =
        update_token_pool_internal_checks token_address_b store in
      { store with token_pool_b = (fa2_balance_callback token_pool) }
    | FA12InternalB token_pool ->
      let () =
        update_token_pool_internal_checks token_address_b store in
      { store with token_pool_b = token_pool }
    | UpdateTokenEnded -> { store with self_is_updating_token_pool = false } in
  (([] : operation list), new_store)

#endif