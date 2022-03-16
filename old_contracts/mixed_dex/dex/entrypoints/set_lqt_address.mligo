#if !DEX_SET_LQT_ADDRESS
#define DEX_SET_LQT_ADDRESS

let set_lqt_address (param : address) (store : storage) : return =
    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.amount > 0mutez then
        (failwith error_AMOUNT_MUST_BE_ZERO : return)
    else if Tezos.sender <> store.manager then
        (failwith error_ONLY_MANAGER_CAN_SET_LQT_ADRESS : return)
    else if store.lqt_address <> ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address) then
        (failwith error_LQT_ADDRESS_ALREADY_SET : return)
 //   else if Tezos.sender <> store.multisig then
 //     let sender_address = Tezos.self_address in
 //     let func () =
 //       match (Tezos.get_entrypoint_opt "%setLqtAddress" sender_address : address contract option) with
 //         | None -> (failwith("no setLqtAddress entrypoint") : operation list)
 //         | Some set_lqt_address_entrypoint ->
 //           [Tezos.transaction param 0mutez set_lqt_address_entrypoint]
 //       in
 //       (prepare_multisig "setLqtAddress" param func store), store
    else 
        (([] : operation list), {store with lqt_address = param})

#endif