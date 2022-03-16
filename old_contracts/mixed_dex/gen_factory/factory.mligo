#include "factory_errors.mligo"
#include "factory_interface.mligo"
#include "factory_functions.mligo"
#include "entrypoints/launch_exchange.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/launch_sink.mligo"

let main (action, store : parameter * storage) : return =
match action with
| LaunchExchange p -> launch_exchange p store
| SetLqtAddress p -> set_lqt_address p store
| LaunchSink -> launch_sink store

(*
    TODO: set_baker
    TODO: add get_dex_address view to factory
    TODO: go over sink contract and improve
*)