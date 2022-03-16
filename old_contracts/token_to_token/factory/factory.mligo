#if !FACTORY
#define FACTORY

#include "../common/common_functions.mligo"
#include "../common/common_interface.mligo"
#include "factory_interface.mligo"
#include "factory_errors.mligo"
#include "factory_functions.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/launch_exchange.mligo"
#include "entrypoints/launch_sink.mligo"


let main ((param, storage) : (param * storage)) =
  let () = check_tezos_amount_is_zero () in
  match param with
  | LaunchExchange p -> launch_exchange p storage
  | LaunchSink -> launch_sink storage
  | SetLqtAddress p -> set_lqt_address p storage

#endif