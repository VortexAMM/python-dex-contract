#include "dex_errors.mligo"
#include "dex_interface.mligo"
#include "dex_functions.mligo"
#include "entrypoints/add_liquidity.mligo"
#include "entrypoints/remove_liquidity.mligo"
#include "entrypoints/set_baker.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/swap.mligo"
#include "entrypoints/update_reserve.mligo"
#include "entrypoints/update_token_pool_internal.mligo"
#include "entrypoints/update_token_pool.mligo"
#include "entrypoints/set_rewards_address.mligo"
#include "entrypoints/default.mligo"


let main (action, store : parameter * storage) : return =
match action with
| Default -> default store
| AddLiquidity p -> add_liquidity p store
| RemoveLiquidity p -> remove_liquidity p store
| SetBaker p -> set_baker p store
| SetLqtAddress p -> set_lqt_address p store
| Swap p -> swap p store
| UpadteReserve p -> update_reserve p store
| UpdateTokenPoolInternal p -> update_token_pool_internal p store
| UpdateTokenPool -> update_token_pool store
| SetRewardsAddress p -> set_rewards_address p store