#if !DEX_SET_LQT_ADDRESS
#define DEX_SET_LQT_ADDRESS

let set_lqt_address (lqt_address : address) (storage : storage) : result =
  let () = check_self_is_not_updating_token_pool storage in
  let () = check_sender storage.manager in
  match storage.lqt_address with
  | None ->
    (([] : operation list),
     { storage with lqt_address = (Some lqt_address) })
  | Some _ -> (failwith error_LQT_ADDRESS_ALREADY_SET : result)

#endif