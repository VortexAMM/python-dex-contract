#if !DEX_TOKEN_TO_TOKEN
#define DEX_TOKEN_TO_TOKEN

let token_to_token (param : token_to_token) (store : storage) : return =
    let { output_dexter_contract = output_dexter_contract ;
          min_tokens_bought = min_tokens_bought ;
          to_ = to_ ;
          tokens_sold = tokens_sold ;
          deadline = deadline } = param in

    let outputDexterContract_contract: xtz_to_token contract =
        (match (Tezos.get_entrypoint_opt "%xtzToToken" output_dexter_contract : xtz_to_token contract option) with
            | None -> (failwith error_INVALID_INTERMEDIATE_CONTRACT :  xtz_to_token contract)
            | Some c -> c) in

    if store.self_is_updating_token_pool then
      (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.amount > 0mutez then
      (failwith error_AMOUNT_MUST_BE_ZERO : return)
    else if Tezos.now >= deadline then
      (failwith error_THE_CURRENT_TIME_MUST_BE_LESS_THAN_THE_DEADLINE : return)
    else
        // we don't check that token_pool > 0, because that is impossible unless all liquidity has been removed
        let xtz_bought =
            natural_to_mutez 
            (((tokens_sold * 9972n * (mutez_to_natural store.xtz_pool)) / (store.token_pool * 10000n + (tokens_sold * 9972n)))) in
        let reserve_fee =
            natural_to_mutez (((tokens_sold * 3n * (mutez_to_natural store.xtz_pool)) / (store.token_pool * 10000n + (tokens_sold * 3n)))) in
        let xtz_volume =
            natural_to_mutez (((tokens_sold * (mutez_to_natural store.xtz_pool)) / (store.token_pool + tokens_sold))) in

        let new_token_pool = store.token_pool + tokens_sold in
        let new_xtz_pool = store.xtz_pool - xtz_bought - reserve_fee in
        let history = Big_map.update "token_pool" (Some new_token_pool) store.history in
        let history = Big_map.update "xtz_pool" (Some (mutez_to_natural new_xtz_pool)) history in
        let history = Big_map.update "xtz_volume" (Some (mutez_to_natural xtz_volume)) history in

        let store = {store with token_pool = new_token_pool ;
                                    xtz_pool = new_xtz_pool ;
                                    history = history }  in

        let op1 = token_transfer store Tezos.sender Tezos.self_address tokens_sold in
        let op2 =
          Tezos.transaction
            {to_ = to_; min_tokens_bought = min_tokens_bought; deadline = deadline}
            xtz_bought
            outputDexterContract_contract in
        let op_reserve = xtz_transfer store.reserve reserve_fee in
        let ops = if reserve_fee = 0mutez then [op1; op2 ] else [op1; op2; op_reserve] in
        (ops , store)

#endif