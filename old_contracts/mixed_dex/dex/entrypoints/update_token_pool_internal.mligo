#if !DEX_UPDATE_TOKEN_POOL_INTERNAL
#define DEX_UPDATE_TOKEN_POOL_INTERNAL

let update_token_pool_internal (token_pool : update_token_pool_internal) (store : storage) : return =
    if (not store.self_is_updating_token_pool or sender <> store.token_address) then
      (failwith error_THIS_ENTRYPOINT_MAY_ONLY_BE_CALLED_BY_GETBALANCE_OF_TOKEN_ADDRESS : return)
    else if Tezos.amount > 0mutez then
      (failwith error_AMOUNT_MUST_BE_ZERO : return)
    else
#if FA2 
        let token_pool =
          match token_pool with
          | [] -> (failwith error_INVALID_FA2_BALANCE_RESPONSE : nat)
          | x :: _xs -> x.1 in
#endif
        let store = {store with token_pool = token_pool ; self_is_updating_token_pool = false} in
        (([ ] : operation list), store)

#endif