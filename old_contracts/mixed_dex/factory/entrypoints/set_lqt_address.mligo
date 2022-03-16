#if !FACTORY_SET_LQT_ADDRESS
#define FACTORY_SET_LQT_ADDRESS

let set_lqt_address (self: address) (p: set_lqt_address_param) (s: storage)  =
    if Tezos.sender <> self then
        (failwith "only self can call this entrypoint" : result)
    else
        let set_lqt_address_entrypoint : address contract =
          match (Tezos.get_entrypoint_opt "%setLqtAddress" p.dex_address :  address contract option) with
          | None -> (failwith error_DEX_SET_LQT_ADDRESS_DOES_NOT_EXIST: address contract)
          | Some contract -> contract in
        let set_lqt_address = Tezos.transaction p.lqt_address 0mutez set_lqt_address_entrypoint in
        ([set_lqt_address], s)

#endif