#if !DEX_UPDATE_RESERVE
#define DEX_UPDATE_RESERVE

[@inline]
let update_reserve (param : update_reserve) (store : storage) : return =
  if Tezos.sender <> store.reserve then
    (failwith error_ONLY_RESERVE_CAN_UPDATE_RESERVE : return)
  else
    (([] : operation list), {store with reserve = param})

#endif