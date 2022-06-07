#include "../common/functions.mligo"

[@inline]
let mint_or_burn (store : storage) (target : address) (quantity : int) :
    operation option =
  if quantity = 0 then 
    None
  else
    let lqt_address =
      match store.lqt_address with
      | None -> (failwith(error_LQT_ADDRESS_IS_NOT_SET) : address)
      | Some addr -> addr in
    let lqt_admin : mint_or_burn contract =
      match
        (Tezos.get_entrypoint_opt "%mintOrBurn" lqt_address
          : mint_or_burn contract option)
      with
      | None ->
          (failwith error_LQT_CONTRACT_MUST_HAVE_A_MINT_OR_BURN_ENTRYPOINT
            : mint_or_burn contract)
      | Some contract -> contract
    in
    Some (Tezos.transaction {quantity = quantity; target = target} 0mutez lqt_admin)

[@inline]
let util (x: nat) (y: nat) : nat * nat =
    let plus = x + y in
    let minus = x - y  in
    let plus_2 = plus * plus in
    let plus_4 = plus_2 * plus_2 in
    let plus_8 = plus_4 * plus_4 in
    let plus_7 = plus_8 / plus in
    let minus_2 = minus * minus in
    let minus_4 = minus_2 * minus_2 in
    let minus_8 = minus_4 * minus_4 in
    let minus_7 = if minus = 0 then 0 else minus_8 / minus in
    (* minus_7 + plus_7 should always be positive *)
    (* since x >0 and y > 0, x + y > x - y and therefore (x + y)^7 > (x - y)^7 and (x + y)^7 - (x - y)^7 > 0 *)
    (abs (plus_8 - minus_8), 8n * (abs (minus_7 + plus_7)))


[@inline]
let rec newton (p : newton_param) : nat =
    if p.n = 0 then
        p.dy
    else
        let new_u, new_du_dy = util (p.x + p.dx) (abs (p.y - p.dy)) in //util returns calculation of u and the derivative with respect to y
        (* new_u - p.u > 0 because dy remains an underestimate *)
        let dy = p.dy + abs ((new_u - p.u) / new_du_dy) in
        (* dy is an underestimate because we start at 0 and the utility curve is convex *)
        newton {p with dy = dy ; n = p.n - 1}

[@inline]
let flat (pool_a : nat) (pool_b : nat) (diff_a : nat) : nat =
    let x = pool_a in
    let y = pool_b in
    let u, _ = util x y in
    (newton {x = x; y = y ; dx = diff_a ; dy = 0n ; u = u ; n = 5})

[@inline]
let compute_out_amount (token_in : nat) (in_total : nat) (out_total : nat) (curve : curve_type) : nat =
  let b_out =
    match curve with
    | Product ->
    (token_in * out_total) /
    ((in_total) + token_in) 
    | Flat ->
    (flat in_total out_total token_in) in
  b_out


[@inline]
let get_contract_FA2_balance_of (token_address : address) : balance_of_param contract =
  match (Tezos.get_entrypoint_opt "%balance_of" token_address : balance_of_param contract option) with
  | None ->
    (failwith error_INVALID_FA2_TOKEN_CONTRACT_MISSING_BALANCE_OF : balance_of_param contract)
  | Some contract -> contract


[@inline]
let get_contract_FA12_get_balance (token_address : address) : get_balance_fa12 contract =
  match (Tezos.get_entrypoint_opt "%getBalance" token_address : get_balance_fa12 contract option) with
  | None ->
    (failwith error_INVALID_FA12_TOKEN_CONTRACT_MISSING_GETBALANCE : get_balance_fa12 contract)
  | Some contract -> contract

[@inline]
let fa2_balance_callback (token_pool : fa2_update_token_pool_internal) : nat =
  match token_pool with
  | (_, amt)::[] -> amt
  | _ -> (failwith error_INVALID_FA2_BALANCE_RESPONSE : nat)

[@inline]
let update_token_pool_internal_checks (token_address : address) (store : storage) : unit =
  if
    (not store.self_is_updating_token_pool) ||
    (Tezos.sender <> token_address)
  then
    (failwith
       error_THIS_ENTRYPOINT_MAY_ONLY_BE_CALLED_BY_GETBALANCE_OF_TOKENADDRESS : 
       unit)
  else if Tezos.amount <> 0mutez then
    failwith error_NO_AMOUNT_TO_BE_SENT
  else ()


[@inline]
let deposit_smak (store : storage) (type_to_burn : token_type) (burn_amount : nat) (reserve_amount : nat) (reference_token: token_type) (direction : bool) : operation option list =
  if burn_amount = 0n && reserve_amount = 0n then
    ([] : operation option list)
  else 
      let sink_deposit =
          match (Tezos.get_entrypoint_opt "%deposit" store.sink : sink_deposit_params contract option) with
          | None -> (failwith error_NO_SINK_DEPOSIT_ENTRYPOINT_EXISTS : sink_deposit_params contract)
          | Some contr -> contr in
      let deposit_params =
      {
          token_to_deposit = type_to_burn;
          reference_token = reference_token;
          burn_amount = burn_amount;
          reserve_amount = reserve_amount;
          direction = direction;
      } in
      let xtz_to_deposit =
        if type_to_burn = Xtz then
          natural_to_mutez (burn_amount + reserve_amount)
        else
          0mutez in
      let opt_op_transfer =
        if type_to_burn = Xtz then 
          (None : operation option)
        else
          make_transfer
              type_to_burn
              Tezos.self_address
              store.sink
              (burn_amount + reserve_amount)
          in
      let opt_op_deposit =
        Some
          (Tezos.transaction
            deposit_params
            xtz_to_deposit
            sink_deposit)
        in

      [opt_op_transfer; opt_op_deposit]


[@inline]
let get_user_reward_info (addr : address) (store : storage) : user_reward_info =
    match Big_map.find_opt addr store.user_rewards with
      | None -> {
          reward = 0n; 
          reward_paid = 0n;
        }
      | Some instance -> instance
    
[@inline]
let update_reward (store : storage) : storage =
    let rewards_time = 
      if Tezos.now > store.period_finish then
        store.period_finish
      else 
        Tezos.now in
    let new_reward = 
        abs(rewards_time - store.last_update_time) * store.reward_per_sec in

    let new_reward_per_share = store.reward_per_share + new_reward / store.lqt_total in 
    let new_last_update_time = Tezos.now in 

    let new_store =
      {
        store with
        reward_per_share = new_reward_per_share;
        last_update_time = new_last_update_time;
        reward = new_reward;
      } in

    
      if Tezos.now > store.period_finish then 
        let delta_time = Tezos.now - store.period_finish in 
        let new_reward_per_sec =  store.reward * accurancy_multiplier / abs(delta_time) in 
        let new_reward = abs(delta_time) * new_reward_per_sec in 
        let new_period_finish = store.period_finish + delta_time in 
        let new_reward_per_share = store.reward_per_share + new_reward / store.lqt_total  in 
        let new_reward = 0n in 
        let xtz_pool =
          if store.token_type_a = Xtz then
            store.token_pool_a
          else
            store.token_pool_b in
        let new_total_reward = abs((mutez_to_natural Tezos.balance) - xtz_pool) in
        {
          store with
          reward_per_share = new_reward_per_share;
          last_update_time = new_last_update_time; 
          reward_per_sec = new_reward_per_sec;
          period_finish = new_period_finish;
          reward = new_reward;
          total_reward = new_total_reward;
        } 
      else
        new_store

[@inline]
let update_user_reward (addr : address) (old_balance : nat) (new_balance : nat) (store : storage) : storage =
    let user_reward_info = get_user_reward_info addr store in 
    let current_reward = old_balance * store.reward_per_share in
    let delta_reward = current_reward - user_reward_info.reward_paid in 
    let reward = user_reward_info.reward + abs(delta_reward) in 
    let reward_paid = (new_balance * store.reward_per_share) in 
    let new_user_reward_info = 
      {
          reward = reward;
          reward_paid = reward_paid;
      } in
    let new_user_reward = Big_map.update addr (Some new_user_reward_info) store.user_rewards in

    let new_store = { store with user_rewards  = new_user_reward} in 
    new_store
