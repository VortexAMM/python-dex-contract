#include "../common/interface.mligo"

type history = baker_rewards_history

type provider_data = baker_rewards_provider_data

type storage = baker_rewards_storage

type return = operation list * storage

type add_lqt_param = baker_rewards_add_lqt

type remove_lqt_param = baker_rewards_remove_lqt


type parameter =
| AddLqt of add_lqt_param
| RemoveLqt of remove_lqt_param
| DepositFees
| ClaimReward of address