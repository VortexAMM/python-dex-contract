#if !LQT_GET_BALANCE
#define LQT_GET_BALANCE

let get_balance (param : get_balance_param) (storage : storage) : operation list =
  let value =
    match Big_map.find_opt param.owner storage.tokens with
    | Some value -> value
    | None -> 0n in
  [Tezos.transaction value 0mutez param.callback]

#endif