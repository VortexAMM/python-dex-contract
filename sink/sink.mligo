#if !SINK
#define SINK

#include "sink_errors.mligo"
#include "sink_interface.mligo"
#include "sink_functions.mligo"
#include "entrypoints/deposit.mligo"
#include "entrypoints/claim.mligo"
#include "entrypoints/update_claim_limit.mligo"
#include "entrypoints/add_exchange.mligo"
#include "entrypoints/remove_exchange.mligo"

let main (action, store : parameter * storage) : return =
match action with
| Deposit p -> deposit p store
| Claim p -> claim p store
| UpdateClaimLimit p -> update_claim_limit p store
| AddExchange p -> add_exchange p store
| RemoveExchange p -> remove_exchange p store

#endif