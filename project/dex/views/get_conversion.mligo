type get_conversion =
[@layout:comb]
{
    direction : bool;
    input_amount : nat;
}

[@view] let get_conversion (param, store : get_conversion * storage) : nat =
    let { direction; input_amount } = param in
    let (pool_in, pool_out) = 
        if direction then
            (store.token_pool_a, store.token_pool_b)
        else
            (store.token_pool_b, store.token_pool_a) in
    compute_out_amount input_amount pool_in pool_out store.curve