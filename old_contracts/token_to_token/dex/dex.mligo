#if !DEX_TOKEN2TOKEN
#define DEX_TOKEN2TOKEN

#include "dex_interface.mligo"
#include "dex_errors.mligo"
#include "dex_functions.mligo"
#include "entrypoints/swap.mligo"
#include "entrypoints/add_liquidity.mligo"
#include "entrypoints/remove_liquidity.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/update_token_pool.mligo"
#include "entrypoints/update_token_pool_internal.mligo"

let main ((common, storage) : (common_entrypoint * storage)) : result =
  let () = check_tezos_amount_is_zero () in
  match common with
  | Swap param -> swap param storage
  | AddLiquidity param -> add_liquidity param storage
  | RemoveLiquidity param -> remove_liquidity param storage
  | SetLqtAddress param -> set_lqt_address param storage
  | UpdateTokenPoolInternal param -> update_token_pool_internal param storage
  | UpdateTokenPool -> update_token_pool storage

#endif