let default (store : storage) : return =
    if store.token_type_a <> Xtz && store.token_type_b <> Xtz then
        (failwith(error_NO_AMOUNT_TO_BE_SENT) : return)
    else
        match store.baker_rewards with
        | None -> (failwith(error_BAKER_REWARDS_ADDRESS_IS_NOT_SET) : return)
        | Some baker_rewards ->
        let reserve_deposit =
            match (Tezos.get_entrypoint_opt "%depositFees" baker_rewards : unit contract option) with
            | None -> (failwith(error_BAKER_REWARDS_ADDRESS_HAS_NO_DEPOSITFEES_ENTRYPOINT) : unit contract)
            | Some contr -> contr in
        [Tezos.transaction () Tezos.amount reserve_deposit], store

