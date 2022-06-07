#include "factory_errors.mligo"
#include "factory_interface.mligo"
#include "factory_functions.mligo"
#include "entrypoints/launch_exchange.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/launch_sink.mligo"
#include "entrypoints/set_baker.mligo"
#include "entrypoints/set_sink_claim_limit.mligo"
#include "entrypoints/update_sink_address.mligo"
#include "entrypoints/remove_exchange.mligo"
#include "entrypoints/update_baker.mligo"
#include "entrypoints/update_multisig.mligo"
#include "views/get_dex_address.mligo"
#include "views/get_dex_by_index.mligo"

let main (action, store : parameter * storage) : return =
match action with
| LaunchExchange p -> launch_exchange p store
| SetLqtAddress p -> set_lqt_address p store
| LaunchSink -> launch_sink store
| SetBaker p -> set_baker p store
| SetSinkClaimLimit p -> set_sink_claim_limit p store
| UpdateSinkAddress p -> update_sink_address p store
| RemoveExchange p -> remove_exchange p store
| UpdateBaker p -> update_baker p store
| UpdateMultisig p -> update_multisig p store
