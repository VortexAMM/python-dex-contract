#if !FACTORY_FUNCTIONS
#define FACTORY_FUNCTIONS

let deploy_dex (init_storage : dex_storage) : (operation * address) =
  [%Michelson ({| {  UNPPAIIR ;
                     CREATE_CONTRACT
#if FA2
#include "../../michelson/dex_fa2.tz"
#else
#include "../../michelson/dex_fa12.tz"
#endif
;
                     PAIR } |} : ((key_hash option) * tez * dex_storage) -> (operation * address))] ((None : key_hash option), Tezos.amount, init_storage)



let deploy_lp_token (init_storage : lp_token_storage) : (operation * address) =
  [%Michelson ({| {  UNPPAIIR ;
                     CREATE_CONTRACT
#include "../../michelson/lqt_fa12.tz"
;
                     PAIR } |} : ((key_hash option) * tez * lp_token_storage) -> (operation * address))] ((None : key_hash option), 0tez, init_storage)



let sqrt (y: nat) =
    if y > 3n then
        let z = y in
        let x = y / 2n + 1n in
        let rec iter (x, y, z: nat * nat * nat): nat =
            if x < z then
                iter ((y / x + x) / 2n, y, x)
            else
                z
        in
        iter (x, y, z)
    else if y <> 0n then
        1n
    else
        0n

[@inline]
let mutez_to_natural (a: tez) : nat =  a / 1mutez

#endif