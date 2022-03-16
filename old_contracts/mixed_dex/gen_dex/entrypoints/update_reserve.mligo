let update_reserve (param : update_reserve_param) (store : storage) : return =
    if Tezos.sender <> store.reserve then
    (failwith error_ONLY_RESERVE_CAN_UPDATE_RESERVE : return)
  else
    (([] : operation list), {store with reserve = param})