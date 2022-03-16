#include "dex_errors.mligo"
#include "dex_interface.mligo"
#include "dex_functions.mligo"
#include "../common/errors.mligo"
#include "../common/interface.mligo"
#include "../common/functions.mligo"
#include "entrypoints/update_reserve.mligo"
#include "entrypoints/add_liquidity.mligo"
#include "entrypoints/remove_liquidity.mligo"
#include "entrypoints/set_baker.mligo"
#include "entrypoints/set_manager.mligo"
#include "entrypoints/set_lqt_address.mligo"
#include "entrypoints/default.mligo"
#include "entrypoints/update_token_pool.mligo"
#include "entrypoints/xtz_to_token.mligo"
#include "entrypoints/token_to_xtz.mligo"
#include "entrypoints/token_to_token.mligo"
#include "entrypoints/update_token_pool_internal.mligo"


let main ((entrypoint, store) : entrypoint * storage) : return =
    match entrypoint with
    | UpdateReserve param -> update_reserve param store
    | AddLiquidity param -> add_liquidity param store
    | RemoveLiquidity param -> remove_liquidity param store
    | SetBaker param -> set_baker param store
    | SetManager param -> set_manager param store
    | SetLqtAddress param -> set_lqt_address param store
    | Default -> default_ store
    | UpdateTokenPool  -> update_token_pool store
    | XtzToToken param -> xtz_to_token param store
    | TokenToXtz param -> token_to_xtz param store
    | TokenToToken param -> token_to_token param store
    | UpdateTokenPoolInternal token_pool -> update_token_pool_internal token_pool store

