#if !COMMON_FUNCTIONS
#define COMMON_FUNCTIONS

[@inline]
let natural_to_mutez (a : nat) : tez = a * 1mutez

[@inline]
let mutez_to_natural (a: tez) : nat =  a / 1mutez

[@inline]
let is_a_nat (i : int) : nat option = Michelson.is_nat i

//[@inline]
//let check_tokens_equal (a : token_type) (b : token_type) =
//  match (a, b) with
//  | (Fa12 addr_a, Fa12 addr_b) -> addr_a = addr_b
//  | (Fa2 (addr_a, i), Fa2 (addr_b, j)) -> addr_a = addr_b && i = j
//  | (Xtz, Xtz) -> true
//  | _ -> false

[@inline]
let get_contract_FA12_transfer (addr : address) : fa12_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" addr : fa12_contract_transfer contract option) with
    | None -> (failwith(error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT) : fa12_contract_transfer contract)
    | Some contract -> contract

[@inline]
let get_contract_FA2_transfer (addr : address) : (fa2_contract_transfer list) contract =
    match (Tezos.get_entrypoint_opt "%transfer" addr : (fa2_contract_transfer list) contract option) with
    | None -> (failwith error_FA2_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : (fa2_contract_transfer list) contract)
    | Some contract -> contract

 [@inline]
 let get_contract_tez_to (addr : address) : unit contract =
   match (Tezos.get_contract_opt addr : unit contract option) with
   | None -> (failwith error_NO_UNIT_CONTRACT : unit contract)
   | Some contract -> contract

[@inline]
let opt_to_op_list (opt_list : (operation option) list) : operation list =
    let ops = ([] : operation list) in
    List.fold (fun (l, op : operation list * operation option) ->
                match op with
                | None -> l
                | Some o -> o :: l) opt_list ops



[@inline]
let make_transfer (opt_id : token_type) (from_addr : address) (to_addr : address) (token_amount : nat) :
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
          | Xtz -> 
              if to_addr = Tezos.self_address then
                  None
              else
                  Some (Tezos.transaction () (natural_to_mutez token_amount) (get_contract_tez_to to_addr)) 

#endif