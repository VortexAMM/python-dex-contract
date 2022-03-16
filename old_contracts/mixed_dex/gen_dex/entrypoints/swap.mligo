let swap (param : swap_param) (store : storage) : return =
    let {t2t_to; tokens_sold; min_tokens_bought; a_to_b; deadline} = param in
    if store.self_is_updating_token_pool then
        (failwith error_SELF_IS_UPDATING_TOKEN_POOL : return)
    else if Tezos.now > deadline then
        (failwith error_SWAP_DEADLINE_IS_OVER : return)
    else
        let aorb_is_smak = a_or_b_is_SMAK store in

        let (bought, feeA_SMAK, feeB_SMAK) =
  match aorb_is_smak with
  | Some aorb_is_smak ->
    compute_out_amount_when_A_or_B_is_SMAK a_to_b aorb_is_smak tokens_sold 
      (if a_to_b then store.token_pool_a else store.token_pool_b)
      (if a_to_b then store.token_pool_b else store.token_pool_a)
      store.curve
  | None ->
    let reduce = match store.curve with
    | Flat -> 9990n
    | Product -> 9972n in
    if a_to_b
    then
      ((compute_out_amount (tokens_sold * reduce) store.token_pool_a
          store.token_pool_b store.curve), 0n, 0n)
    else
      ((compute_out_amount (tokens_sold * reduce) store.token_pool_b
          store.token_pool_a store.curve), 0n, 0n) in

    if bought < min_tokens_bought then
        (failwith error_TOKENS_BOUGHT_MUST_BE_GREATER_THAN_OR_EQUAL_TO_MIN_TOKENS_BOUGHT : return)
    else
        let (new_pool_a, new_pool_b) =
    if a_to_b then
      (* A to B *)
      ( store.token_pool_a + tokens_sold - feeA_SMAK,
        store.token_pool_b - bought - feeB_SMAK )
    else
      (* B to A *)
      ( store.token_pool_a - bought - feeA_SMAK,
        store.token_pool_b + tokens_sold - feeB_SMAK) in
    let new_pool_a =
        match is_nat new_pool_a with
        | None ->
            (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : nat)
        | Some difference -> difference in
    let new_pool_b =
        match is_nat new_pool_b with
        | None ->
            (failwith error_TOKEN_POOL_MINUS_TOKENS_BOUGHT_IS_NEGATIVE : nat)
        | Some difference -> difference in
        let (op_token_a_transfer, op_token_b_transfer) =
            if a_to_b then
              (* A to B *)
                ( 
                make_transfer
                    store.token_type_a
                    Tezos.sender
                    Tezos.self_address
                    tokens_sold,
                make_transfer
                    store.token_type_b 
                    Tezos.self_address
                    t2t_to
                    bought 
                )
            else
              (* B to A *)
                (
                make_transfer 
                    store.token_type_a 
                    Tezos.self_address
                    t2t_to 
                    bought,
                make_transfer
                    store.token_type_b
                    Tezos.sender
                    Tezos.self_address
                    tokens_sold 
                ) in
        
        let ops =
            opt_to_op_list [op_token_a_transfer; op_token_b_transfer] in
        let new_history =
            Big_map.update "token_pool_a" (Some new_pool_a) store.history in
        let new_history =
            Big_map.update "token_pool_b" (Some new_pool_b) new_history in
        let amounts_and_fees_out =
            compute_fees store new_pool_a new_pool_b feeA_SMAK feeB_SMAK in
        let ops_pay_fees_opt =
            withdraw_or_burn_fees
                store
                amounts_and_fees_out.reserve_fee_in_A
                amounts_and_fees_out.reserve_fee_in_B in
        let ops_pay_fees = opt_to_op_list ops_pay_fees_opt in
        let ops = List.fold (fun(l, op : operation list * operation) -> op :: l) ops ops_pay_fees in
        let new_store =
            {
                store with
                token_pool_a = amounts_and_fees_out.amount_in_A;
                token_pool_b = amounts_and_fees_out.amount_in_B;
                history = new_history;
                last_k = amounts_and_fees_out.amount_in_A * amounts_and_fees_out.amount_in_B;
            } in
        ops, new_store