#if !SINK_DEPOSIT
#define SINK_DEPOSIT

let deposit (param : sink_deposit_params) (store : storage) : return =
    let {
            token_to_deposit;
            reference_token;
            burn_amount;
            reserve_amount;
            direction;
        } = param in
    let dex_address =
        if direction then
            match Big_map.find_opt (token_to_deposit, reference_token) store.exchanges with
            | None -> (failwith(error_PAIR_DOES_NOT_EXIST) : address)
            | Some addr -> addr
        else
            match Big_map.find_opt (reference_token, token_to_deposit) store.exchanges with
            | None -> (failwith(error_PAIR_DOES_NOT_EXIST) : address)
            | Some addr -> addr in
    if Tezos.sender <> dex_address then
        (failwith(error_ONLY_EXCHANGES_CAN_DEPOSIT) : return)
    else
        let new_burn =
            match Big_map.find_opt token_to_deposit store.burn with
            | None -> Big_map.update token_to_deposit (Some burn_amount) store.burn
            | Some amt -> Big_map.update token_to_deposit (Some (amt + burn_amount)) store.burn in
        let new_reserve =
            match Big_map.find_opt token_to_deposit store.reserve with
            | None -> Big_map.update token_to_deposit (Some reserve_amount) store.reserve
            | Some amt -> Big_map.update token_to_deposit (Some (amt + reserve_amount)) store.reserve in
        let new_store = { store with burn = new_burn; reserve = new_reserve } in
        ([] : operation list), new_store

#endif