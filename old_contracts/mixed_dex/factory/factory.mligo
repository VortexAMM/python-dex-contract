#include "factory_errors.mligo"
#include "factory_interface.mligo"
#include "factory_functions.mligo"
#include "entrypoints/launch_exchange_mixed.mligo"
#include "entrypoints/set_lqt_address.mligo"

let main ((param, storage) : param * storage) =
    match param with
    | LaunchExchangeMixed p -> launch_exchange_mixed Tezos.self_address p storage
    | SetLqtAddress p -> set_lqt_address Tezos.self_address p storage
