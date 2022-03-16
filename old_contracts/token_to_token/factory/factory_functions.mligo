#if !FACTORY_FUNCTIONS
#define FACTORY_FUNCTIONS

let deploy_dex (init_storage : dex_storage) : (operation * address) =
  ([%Michelson
    ({| {  UNPPAIIR ;
             CREATE_CONTRACT
#include "../../michelson/t2t_dex.tz"
  ;
            PAIR } |} : 
       (key_hash option * tez * dex_storage) -> (operation * address))])
    ((None : key_hash option), Tezos.amount, init_storage)

let deploy_sink (init_storage : sink_storage) : (operation * address) =
  ([%Michelson
    ({| {  UNPPAIIR ;
           CREATE_CONTRACT
#include "../../michelson/sink.tz"
  ;
           PAIR } |} : 
       (key_hash option * tez * sink_storage) -> (operation * address))])
    ((None : key_hash option), 0tez, init_storage)

let deploy_lp_token (init_storage : lp_token_storage) : (operation * address) =
  ([%Michelson
    ({| {  UNPPAIIR ;
           CREATE_CONTRACT
#include "../../michelson/lqt_fa12.tz"
  ;
           PAIR } |} : 
       (key_hash option * tez * lp_token_storage) -> (operation * address))])
    ((None : key_hash option), 0tez, init_storage)


[@view]
let get_dex_address ((p, storage) : (get_address_param * storage)) : address =
  let (a, a_id, b, b_id) =
    if p.direction
    then (p.a_addr, p.a_id, p.b_addr, p.b_id)
    else (p.b_addr, p.b_id, p.a_addr, p.a_id) in
  match Big_map.find_opt ((a, a_id), (b, b_id)) storage.pairs with
  | None -> (failwith error_DEX_ADDRESS_NOT_FOUND_IN_FACTORY : address)
  | Some addr -> (addr : address)

#endif