
#include "baker_rewards_errors.mligo"
#include "baker_rewards_interface.mligo"
#include "baker_rewards_functions.mligo"
#include "entrypoints/deposit_fees.mligo"
#include "entrypoints/add_lqt.mligo"
#include "entrypoints/remove_lqt.mligo"
#include "entrypoints/claim_reward.mligo"


let main (action, store : parameter * storage) : return =
match action with
| AddLqt p -> add_lqt p store
| RemoveLqt p -> remove_lqt p store
| DepositFees -> deposit_fees store
| ClaimReward p -> claim_reward p store