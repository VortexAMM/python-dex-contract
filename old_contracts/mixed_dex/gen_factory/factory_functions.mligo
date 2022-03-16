#include "../gen_common/functions.mligo"

[@inline]
let mutez_to_natural (a: tez) : nat =  a / 1mutez

[@inline]
let sqrt (y : nat) =
  if y > 3n then
    let z = y in
    let x = (y / 2n) + 1n in
    let rec iter : nat * nat * nat -> nat =
     fun ((x : nat), (y : nat), (z : nat)) ->
      if x < z then iter (((y / x) + x) / 2n, y, x) else z
    in
    iter (x, y, z)
  else if y <> 0n then 1n
  else 0n

[@inline]
let check_tokens_equal (type_a : token_type) (type_b : token_type) =
  match (type_a, type_b) with
  | (Fa12 i, Fa12 j) -> i = j
  | (Fa2 (i1, i2), Fa2 (j1, j2)) -> i1 = j1 && i2 = j2
  | (Xtz, Xtz) -> true
  | _ -> false

let deploy_dex (init_storage : dex_storage) : (operation * address) =
  ([%Michelson
    ({| {  UNPPAIIR ;
             CREATE_CONTRACT
#include "../../michelson/gen_dex.tz"
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