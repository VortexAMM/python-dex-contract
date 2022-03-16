#if !DEX_ADD_LIQUIDITY
#define DEX_ADD_LIQUIDITY

let add_liquidity (param : add_liquidity) (store: storage) : return =
    let { owner = owner ;
          min_lqt_minted = min_lqt_minted ;
          max_tokens_deposited = max_tokens_deposited ;
          deadline = deadline } = param in

    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.now >= deadline then
        (failwith error_THE_CURRENT_TIME_MUST_BE_LESS_THAN_THE_DEADLINE : return)
    else
        // the contract is initialized, use the existing exchange rate
        // mints nothing if the contract has been emptied, but that's OK
        let xtz_pool   : nat = mutez_to_natural store.xtz_pool in
        let nat_amount : nat = mutez_to_natural Tezos.amount  in
        let lqt_minted : nat = nat_amount * store.lqt_total  / xtz_pool in
        let tokens_deposited : nat = ceildiv (nat_amount * store.token_pool) xtz_pool in

        if tokens_deposited > max_tokens_deposited then
            (failwith error_MAX_TOKENS_DEPOSITED_MUST_BE_GREATER_THAN_OR_EQUAL_TO_TOKENS_DEPOSITED : return)
        else if lqt_minted < min_lqt_minted then
            (failwith error_LQT_MINTED_MUST_BE_GREATER_THAN_MIN_LQT_MINTED : return)
        else
            let store = {store with
                lqt_total  = store.lqt_total + lqt_minted ;
                token_pool = store.token_pool + tokens_deposited ;
                xtz_pool   = store.xtz_pool + Tezos.amount} in

            let history = Big_map.update "token_pool" (Some store.token_pool) store.history in
            let history = Big_map.update "xtz_pool" (Some (mutez_to_natural store.xtz_pool)) history in
            let history = Big_map.update "token_pool" (Some store.token_pool) history in

            let investment = 
                { 
                    xtz= Tezos.amount; 
                    token=tokens_deposited; 
                    direction=Add
                } in
            let user_investments = Big_map.update Tezos.sender (Some investment) store.user_investments in
            let store = { store with history = history ; user_investments = user_investments } in

            // send tokens from sender to exchange
            let op_token = token_transfer store Tezos.sender Tezos.self_address tokens_deposited in
            // mint lqt tokens for them
            let op_lqt = mint_or_burn store owner (int lqt_minted) in
            ([op_token; op_lqt], store)

#endif