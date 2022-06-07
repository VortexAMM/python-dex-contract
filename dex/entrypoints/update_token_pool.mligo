[@inline]
let fa2_balance_callback (token_pool : fa2_update_token_pool_internal) : nat =
  match token_pool with
  | (_, amt)::[] -> amt
  | _ -> (failwith error_INVALID_FA2_BALANCE_RESPONSE : nat)

[@inline]
let get_entrypoint_A2 () : balance_of_response list contract option =
  (Tezos.get_entrypoint_opt "%fA2InternalA" Tezos.self_address : balance_of_response list contract option)

[@inline]
let get_entrypoint_A12 () : nat contract option =
  (Tezos.get_entrypoint_opt "%fA12InternalA" Tezos.self_address : nat contract option)

[@inline]
let get_entrypoint_B2 () : balance_of_response list contract option =
  (Tezos.get_entrypoint_opt "%fA2InternalB" Tezos.self_address : balance_of_response list contract option)

[@inline]
let get_entrypoint_B12 () : nat contract option =
  (Tezos.get_entrypoint_opt "%fA12InternalB" Tezos.self_address : nat contract option)


let update_ended_callback () : operation =
  let my_address = Tezos.self_address in
  match (Tezos.get_entrypoint_opt "%updateTokenEnded" my_address : unit contract option)
  with
  | None -> (failwith error_UPDATETOKENENDED_NOT_FOUND_IN_SELF : operation)
  | Some c -> Tezos.transaction () 0mutez c

[@inline]
let update_token_pool_aux (token_id : fa_token) (get_entrypoint2 : unit -> balance_of_response list contract option) (get_entrypoint12 : unit -> nat contract option) : operation =
  let () = no_xtz in
  let my_address = Tezos.self_address in
  match token_id with
  | FA2 (fa2_address, fa2_token_id) ->
    let token_balance_of : balance_of_param contract =
      get_contract_FA2_balance_of fa2_address in
    let cfmm_update_token_pool_internal : balance_of_response list contract =
      match get_entrypoint2 () with
      | None ->
        (failwith error_NON_EXISTING_ENTRYPOINT2 : balance_of_response list
             contract)
      | Some c -> c in
    Tezos.transaction
      {
        requests = [{ owner = my_address; token_id = fa2_token_id }];
        callback = cfmm_update_token_pool_internal
      } 0mutez token_balance_of
  | FA12 token_address ->
    let token_get_balance : get_balance_fa12 contract =
      get_contract_FA12_get_balance token_address in
    let cfmm_update_token_pool_internal
      : fa12_update_token_pool_internal contract =
      match get_entrypoint12 () with
      | None -> (failwith error_NON_EXISTING_ENTRYPOINT12 : nat contract)
      | Some c -> c in
    Tezos.transaction (my_address, cfmm_update_token_pool_internal) 0mutez
      token_get_balance

[@inline]
let update_token_pool_aux_fa12 (token_address : address) (get_entrypoint12 : unit -> nat contract option) : operation =
  let my_address = Tezos.self_address in
    let token_get_balance : get_balance_fa12 contract =
      get_contract_FA12_get_balance token_address in
    let cfmm_update_token_pool_internal
      : fa12_update_token_pool_internal contract =
      match get_entrypoint12 () with
      | None -> (failwith error_NON_EXISTING_ENTRYPOINT12 : nat contract)
      | Some c -> c in
    Tezos.transaction (my_address, cfmm_update_token_pool_internal) 0mutez
      token_get_balance

[@inline]
let update_token_pool_aux_fa2 (token_address : address) (token_id : nat) (get_entrypoint2 : unit -> balance_of_response list contract option) : operation =
  let my_address = Tezos.self_address in
  let token_balance_of : balance_of_param contract =
      get_contract_FA2_balance_of token_address in
    let cfmm_update_token_pool_internal : balance_of_response list contract =
      match get_entrypoint2 () with
      | None ->
        (failwith error_NON_EXISTING_ENTRYPOINT2 : balance_of_response list
             contract)
      | Some c -> c in
    Tezos.transaction
      {
        requests = [{ owner = my_address; token_id = token_id }];
        callback = cfmm_update_token_pool_internal
      } 0mutez token_balance_of

let update_token_pool (store : storage) : return =
  if Tezos.source <> Tezos.sender then
    (failwith error_CALL_NOT_FROM_AN_IMPLICIT_ACCOUNT : return)
  else if store.self_is_updating_token_pool then 
    (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
  else
  let op_a_opt : operation option =
    match store.token_type_a with
    | Fa12 token_address -> 
    Some (update_token_pool_aux_fa12 token_address
      get_entrypoint_A12)
    | Fa2 (token_address, token_id) ->
    Some (update_token_pool_aux_fa2 token_address token_id
      get_entrypoint_A2)
    | Xtz -> None in
  let op_b_opt : operation option =
    match store.token_type_a with
    | Fa12 token_address -> 
    Some (update_token_pool_aux_fa12 token_address 
      get_entrypoint_B12)
    | Fa2 (token_address, token_id) ->
    Some (update_token_pool_aux_fa2 token_address token_id
      get_entrypoint_B2)
    | Xtz -> None in
  let update_ended  = update_ended_callback () in
  let ops = [update_ended] in
  let ops = 
    match op_b_opt with
    | Some op -> op :: ops
    | None -> ops in
  let ops =
    match op_a_opt with
    | Some op -> op :: ops
    | None -> ops in
  let new_store = { store with self_is_updating_token_pool = true } in
  (ops, new_store)
  