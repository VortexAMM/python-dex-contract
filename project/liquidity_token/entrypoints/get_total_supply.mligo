#if !LQT_GET_TOTAL_SUPPLY
#define LQT_GET_TOTAL_SUPPLY

let get_total_supply (param : get_total_supply_param) (storage : storage) : operation list =
  let total = storage.total_supply in
  [Tezos.transaction total 0mutez param.callback]

#endif