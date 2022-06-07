#include "../common/functions.mligo"

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
#include "../michelson/dex.tz"
  ;
            PAIR } |} : 
       (key_hash option * tez * dex_storage) -> (operation * address))])
    ((None : key_hash option), Tezos.amount, init_storage)

let deploy_sink (init_storage : sink_storage) : (operation * address) =
  ([%Michelson
    ({| {  UNPPAIIR ;
           CREATE_CONTRACT
#include "../michelson/sink.tz"
  ;
           PAIR } |} : 
       (key_hash option * tez * sink_storage) -> (operation * address))])
    ((None : key_hash option), 0tez, init_storage)

let deploy_lp_token (init_storage : lp_token_storage) : (operation * address) =
  ([%Michelson
    ({| {  UNPPAIIR ;
           CREATE_CONTRACT
#include "../michelson/lqt_fa12.tz"
  ;
           PAIR } |} : 
       (key_hash option * tez * lp_token_storage) -> (operation * address))])
    ((None : key_hash option), 0tez, init_storage)


[@inline]
let make_transfer_to_dex (opt_id : token_type) (from_addr : address) (to_addr : address) (token_amount : nat) :
    operation option =
        if token_amount = 0n then None
        else
          match opt_id with
          | Fa12 token_address ->
              let transfer_param =
                {address_from = from_addr; address_to = to_addr; value = token_amount}
              in
              Some
                (Tezos.transaction
                   transfer_param
                   0mutez
                   (get_contract_FA12_transfer token_address))
          | Fa2 (token_address, token_id) -> 
              Some
                (Tezos.transaction
                   [
                     {
                       from_ = from_addr;
                       txs =
                         [
                           {
                             to_ = to_addr;
                             token_id = token_id;
                             amount = token_amount;
                           };
                         ];
                     };
                   ]
                   0mutez
                   (get_contract_FA2_transfer token_address))
          | Xtz -> None

[@inline]
let prepare_multisig (type p) (entrypoint_name: string) (param: p) (func: unit -> operation list) (store : storage) : operation list =
    match (Tezos.get_entrypoint_opt "%callMultisig" store.multisig : call_param contract option ) with
    | None -> (failwith("no call entrypoint") : operation list)
    | Some contract ->
        let packed = Bytes.pack param in
        let param_hash = Crypto.sha256 packed in
        let entrypoint_signature =
          {
            name = entrypoint_name;
            params = param_hash;
            source_contract = Tezos.self_address;
          }
        in
        let call_param =
        {
          entrypoint_signature = entrypoint_signature;
          callback = func;
        }
        in
        let set_storage = Tezos.transaction call_param 0mutez contract in
        [set_storage]