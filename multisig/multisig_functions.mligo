[@inline]
let prepare_multisig (type p) (entrypoint_name: string) (param: p) (func: unit -> operation list) : operation list =
    match (Tezos.get_entrypoint_opt "%callMultisig" Tezos.self_address : call_param contract option ) with
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