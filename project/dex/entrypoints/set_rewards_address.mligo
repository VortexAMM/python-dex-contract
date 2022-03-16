#if !DEX_SET_REWARDS_ADDRESS
#define DEX_SET_REWARDS_ADDRESS

let set_rewards_address (rewards_address : address) (store : storage) : return =
if Tezos.sender <> store.manager then
    (failwith(error_ONLY_MANAGER_CAN_SET_REWARDS_ADDRESS) : return)
else
    ([] : operation list), { store with baker_rewards = (Some rewards_address) }

#endif