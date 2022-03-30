let update_sink_address (param : address) (store : storage) : return =
    if Tezos.sender <> store.manager then
    (failwith error_ONLY_MANAGER_CAN_UPDATE_SINK_ADDRESS : return)
  else
    (([] : operation list), {store with sink = param})