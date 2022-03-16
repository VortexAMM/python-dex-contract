#if !COMMON_FUNCTIONS
#define COMMON_FUNCTIONS

[@inline]
let get_contract_FA2_transfer (token_address : address) :
    fa2_transfer list contract =
  match
    (Tezos.get_entrypoint_opt "%transfer" token_address
      : fa2_transfer list contract option)
  with
  | None ->
      (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT_FA2
        : fa2_transfer list contract)
  | Some contract -> contract

[@inline]
let get_contract_FA12_transfer (token_address : address) : fa12_transfer contract = 
  match (Tezos.get_entrypoint_opt "%transfer" token_address : fa12_transfer contract option) with
  | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT_FA12)
  | Some contract -> contract

[@inline]
let prepare_multisig (entrypoint_name: string) (param: _p) (func: unit -> operation list) (store : storage) : operation list =
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

#endif