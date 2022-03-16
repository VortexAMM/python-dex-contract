#if !DEX_XTZ_TO_TOKEN
#define DEX_XTZ_TO_TOKEN

let xtz_to_token (param : xtz_to_token) (store : storage) : return =
   let { to_ = to_ ;
         min_tokens_bought = min_tokens_bought ;
         deadline = deadline } = param in

    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.now >= deadline then
        (failwith error_THE_CURRENT_TIME_MUST_BE_LESS_THAN_THE_DEADLINE : return)
    else begin
        // we don't check that xtz_pool > 0, because that is impossible
        // unless all liquidity has been removed
        let xtz_pool = mutez_to_natural store.xtz_pool in
        let nat_amount = mutez_to_natural Tezos.amount in
        let tokens_bought =
            let bought = 
                (nat_amount * 9972n * store.token_pool) / (xtz_pool * 10000n + (nat_amount * 9972n)) in
            if bought < min_tokens_bought then
                (failwith error_TOKENS_BOUGHT_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_BOUGHT : nat)
            else
                bought
        in
        let reserve_fee = natural_to_mutez (nat_amount * 3n / 10000n) in
        let new_token_pool = (match is_nat (store.token_pool - tokens_bought) with
            | None -> (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : nat)
            | Some difference -> difference) in
        let new_xtz_pool = store.xtz_pool + Tezos.amount - reserve_fee in

        // update xtz_pool
        let store = { store with xtz_pool = new_xtz_pool ; token_pool = new_token_pool } in
        let history = Big_map.update "token_pool" (Some store.token_pool) store.history in
        let history = Big_map.update "xtz_pool" (Some (mutez_to_natural store.xtz_pool)) history in
        let history = Big_map.update "xtz_volume" (Some nat_amount) history in
        let store = { store with history = history } in
        // send tokens_withdrawn to to address
        // if tokens_bought is greater than storage.token_pool, this will fail
        let op = token_transfer store Tezos.self_address to_ tokens_bought in
        let op_tez_to_reserve = xtz_transfer store.reserve reserve_fee in

        let ops = if reserve_fee = 0mutez then [ op ] else [ op; op_tez_to_reserve ] in
        (ops, store)
    end

#endif