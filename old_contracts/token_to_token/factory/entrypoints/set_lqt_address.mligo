#if !SET_LQT_ADDRESS
#define SET_LQT_ADDRESS

[@inline]
let set_lqt_address (lqt_param : set_lqt_address_param) (storage : storage) =
  let () = check_sender Tezos.self_address in
  let set_lqt_address_entrypoint : address contract =
    match (Tezos.get_entrypoint_opt "%setLqtAddress" lqt_param.dex_address : 
             address contract option)
    with
    | None ->
      (failwith error_DEX_SET_LQT_ADDRESS_DOES_NOT_EXIST : address contract)
    | Some contract -> contract in
  let set_lqt_address =
    Tezos.transaction lqt_param.lqt_address 0mutez set_lqt_address_entrypoint in
  ([set_lqt_address], storage)

#endif