#include "lqt_interface.mligo"
#include "lqt_functions.mligo"
#include "entrypoints/transfer.mligo"
#include "entrypoints/approve.mligo"
#include "entrypoints/mint_or_burn.mligo"
#include "entrypoints/get_allowance.mligo"
#include "entrypoints/get_balance.mligo"
#include "entrypoints/get_total_supply.mligo"

let main (param, storage : parameter * storage) : return =
    if Tezos.amount <> 0mutez
      then failwith "DontSendTez"
    else
      match param with
      | Transfer param -> transfer param storage
      | Approve param -> approve param storage
      | MintOrBurn param -> mint_or_burn param storage
      | GetAllowance param -> (get_allowance param storage, storage)
      | GetBalance param -> (get_balance param storage, storage)
      | GetTotalSupply param -> (get_total_supply param storage, storage)

