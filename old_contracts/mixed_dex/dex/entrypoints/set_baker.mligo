#if !DEX_SET_BAKER
#define DEX_SET_BAKER

let set_baker (param : set_baker) (store : storage) : return =
    if store.self_is_updating_token_pool then
      (failwith error_SELF_IS_UPDATING_TOKEN_POOL_MUST_BE_FALSE : return)
    else if Tezos.amount > 0mutez then
       (failwith error_AMOUNT_MUST_BE_ZERO  : return)
    else if store.freeze_baker then
        (failwith error_BAKER_PERMANENTLY_FROZEN : return)
    else if Tezos.sender <> store.multisig then
      let sender_address = Tezos.self_address in
      let func () =
        match (Tezos.get_entrypoint_opt "%setBaker" sender_address : set_baker contract option) with
          | None -> (failwith("no setBaker entrypoint") : operation list)
          | Some set_baker_entrypoint ->
            [Tezos.transaction param 0mutez set_baker_entrypoint]
        in
        (prepare_multisig "setBaker" param func store), store
    else
        let { 
                baker = baker ;
                freeze_baker = freeze_baker 
            } = param in
        ([ Tezos.set_delegate baker ], {store with freeze_baker = freeze_baker})

#endif