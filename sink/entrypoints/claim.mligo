#if !SINK_CLAIM
#define SINK_CLAIM


let claim (param : claim_param) (store : storage) : return =
    let {
        reward_to;
        tokens;
        deadline;
        } = param in
    let ops = ([] : operation list) in
    if List.size tokens = 0n then
        (failwith(error_TOKEN_LIST_EMPTY) : return)
    else if List.size tokens >= store.token_claim_limit then
        (failwith(error_TOKEN_LIST_TOO_LARGE) : return)
    else
        let ops =
            List.fold (fun (op_list, token : operation list * token_type) -> 
                let (dex_addr, swap_direction) =
                    match Big_map.find_opt (token, store.token_type_smak) store.exchanges with
                    | Some dex_addr -> (dex_addr, true)
                    | None -> 
                        let reverse_pair =
                            match Big_map.find_opt (store.token_type_smak, token) store.exchanges with
                            | Some dex_addr -> (dex_addr, false)
                            | None -> (failwith(error_NO_SMAK_TO_TOKEN_DEX) : address * bool) in
                        reverse_pair in
    
                let to_burn =
                    match Big_map.find_opt token store.burn with
                    | None -> (failwith(error_TOKEN_TO_BURN_NOT_LISTED) : nat)
                    | Some amt -> amt in
    
                let to_reserve =
                    match Big_map.find_opt token store.reserve with
                    | None -> (failwith(error_TOKEN_TO_RESERVE_NOT_LISTED) : nat) // UNREACHABLE
                    | Some amt -> amt in
    
                let op_reserve = 
                    make_transfer
                        token 
                        Tezos.self_address
                        store.reserve_address
                        to_reserve in
                
                let op_list =
                    match op_reserve with
                    | None -> op_list
                    | Some op -> op :: op_list in
    
                let xtz_to_send_swap =
                    if token = Xtz then
                        natural_to_mutez to_burn
                    else
                        0mutez in
                let op_swap =
                    external_swap
                        dex_addr
                        ({
                            t2t_to = reward_to;
                            tokens_sold = to_burn;
                            min_tokens_bought = 0n;
                            a_to_b = swap_direction;
                            deadline = deadline;
                        } : dex_swap_param)
                        xtz_to_send_swap in
                let op_list = if to_burn <> 0n then
                    op_swap :: op_list
                else
                    op_list in
    
                let op_list =
                    if to_burn + to_reserve <> 0n then
                        match token with
                        | Fa12 token_address -> external_approve_fa12 token_address dex_addr (to_burn + to_reserve) :: op_list
                        | _ -> op_list
                    else
                        op_list in
                op_list
                ) tokens ops in
        ops, store

#endif

