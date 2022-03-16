#include "factory_errors.mligo"
#include "factory_interface.mligo"
#include "factory_functions.mligo"
#include "entrypoints/launch_exchange.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/set_rewards_address.mligo"
#include "entrypoints/launch_sink.mligo"
#include "entrypoints/set_baker.mligo"
#include "entrypoints/set_sink_claim_limit.mligo"
#include "views/get_dex_address.mligo"

let main (action, store : parameter * storage) : return =
match action with
| LaunchExchange p -> launch_exchange p store
| SetLqtAddress p -> set_lqt_address p store
| SetRewardsAddress p -> set_rewards_address p store
| LaunchSink -> launch_sink store
| SetBaker p -> set_baker p store
| SetSinkClaimLimit p -> set_sink_claim_limit p store
