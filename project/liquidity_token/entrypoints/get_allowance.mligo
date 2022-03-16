#if !LQT_GET_ALLOWANCE
#define LQT_GET_ALLOWANCE

let get_allowance (param : get_allowance_param) (storage : storage) : operation list =
  let value =
    match Big_map.find_opt param.request storage.allowances with
    | Some value -> value
    | None -> 0n in
  [Tezos.transaction value 0mutez param.callback]

#endif