#if !DEX_UPDATE_TOKEN_POOL
#define DEX_UPDATE_TOKEN_POOL

let update_token_pool (store : storage) : return =
    if Tezos.sender <> Tezos.source then
        (failwith error_CALL_NOT_FROM_AN_IMPLICIT_ACCOUNT : return)
    else if Tezos.amount > 0mutez then
      (failwith error_AMOUNT_MUST_BE_ZERO : return)
    else if store.self_is_updating_token_pool then
      (failwith error_UNEXPECTED_REENTRANCE_IN_UPDATE_TOKEN_POOL : return)
    else
      let cfmm_update_token_pool_internal : update_token_pool_internal contract = Tezos.self "%updateTokenPoolInternal"  in
#if FA2
      let token_balance_of : balance_of contract = (match
        (Tezos.get_entrypoint_opt "%balance_of" store.token_address : balance_of contract option) with
        | None -> (failwith error_INVALID_FA2_TOKEN_CONTRACT_MISSING_BALANCE_OF : balance_of contract)
        | Some contract -> contract) in
      let op = Tezos.transaction ([(Tezos.self_address, store.token_id)], cfmm_update_token_pool_internal) 0mutez token_balance_of in
#else
      let token_get_balance : get_balance contract = (match
        (Tezos.get_entrypoint_opt "%getBalance" store.token_address : get_balance contract option) with
        | None -> (failwith error_INVALID_FA12_TOKEN_CONTRACT_MISSING_GETBALANCE : get_balance contract)
        | Some contract -> contract) in
      let op = Tezos.transaction (Tezos.self_address, cfmm_update_token_pool_internal) 0mutez token_get_balance in
#endif
      ([ op ], {store with self_is_updating_token_pool = true})

#endif