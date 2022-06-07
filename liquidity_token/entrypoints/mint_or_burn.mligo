#if !LQT_MINT_OR_BURN
#define LQT_MINT_OR_BURN

let mint_or_burn (param : mint_or_burn_param) (storage : storage) : return =
    if Tezos.sender <> storage.admin
      then failwith "OnlyAdmin"
    else
      let tokens = storage.tokens in
      let old_balance =
        match Big_map.find_opt param.target tokens with
        | None -> 0n
        | Some bal -> bal in
      let new_balance =
        match is_nat (old_balance + param.quantity) with
        | None -> (failwith "Cannot burn more than the target's balance." : nat)
        | Some bal -> bal in
      let tokens = Big_map.update param.target (maybe new_balance) storage.tokens in
      let total_supply = abs (storage.total_supply + param.quantity) in
      (([] : operation list), { storage with tokens = tokens ; total_supply = total_supply })

#endif