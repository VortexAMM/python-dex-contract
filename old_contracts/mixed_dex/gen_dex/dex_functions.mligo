[@inline]
let natural_to_mutez (a: nat): tez = a * 1mutez

[@inline]
let is_a_nat (i : int) : nat option = Michelson.is_nat i

[@inline]
let ceildiv (numerator : nat) (denominator : nat) : nat =
  match ediv numerator denominator with
  | None -> (failwith "DIV by 0" : nat)
  | Some v ->
      let (q, r) = v in
      if r = 0n then q else q + 1n

[@inline]
let sqrt (y : nat) =
  if y > 3n then
    let z = y in
    let x = (y / 2n) + 1n in
    let rec iter : nat * nat * nat -> nat =
     fun ((x : nat), (y : nat), (z : nat)) ->
      if x < z then iter (((y / x) + x) / 2n, y, x) else z
    in
    iter (x, y, z)
  else if y <> 0n then 1n
  else 0n

type transfer_direction = 
| In
| Out

type fa12_contract_transfer =
[@layout:comb]
{
    [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat; 
}

type transfer_destination =
[@layout:comb]
{
  to_ : address;
  token_id : token_id;
  amount : nat;
}

type fa2_contract_transfer =
[@layout:comb]
{
  from_ : address;
  txs : transfer_destination list;
}

[@inline]
let check_tokens_equal (a : token_type) (b : token_type) =
  match (a, b) with
  | (Fa12 addr_a, Fa12 addr_b) -> addr_a = addr_b
  | (Fa2 (addr_a, i), Fa2 (addr_b, j)) -> addr_a = addr_b && i = j
  | (Xtz, Xtz) -> true
  | _ -> false

[@inline]
let get_contract_FA12_transfer (addr : address) : fa12_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" addr : fa12_contract_transfer contract option) with
    | None -> (failwith(error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT) : fa12_contract_transfer contract)
    | Some contract -> contract

[@inline]
let get_contract_FA2_transfer (addr : address) : (fa2_contract_transfer list) contract =
    match (Tezos.get_entrypoint_opt "%transfer" addr : (fa2_contract_transfer list) contract option) with
    | None -> (failwith error_FA2_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : (fa2_contract_transfer list) contract)
    | Some contract -> contract

[@inline]
let get_contract_tez_to (addr : address) : unit contract =
    match (Tezos.get_contract_opt addr : unit contract option) with
    | None -> (failwith error_NO_UNIT_CONTRACT : unit contract)
    | Some contract -> contract

[@inline]
let make_transfer (opt_id : token_type) (from_addr : address) (to_addr : address) (token_amount : nat) :
    operation option =
        if token_amount = 0n then None
        else
          match opt_id with
          | Fa12 token_address ->
              let transfer_param =
                {address_from = from_addr; address_to = to_addr; value = token_amount}
              in
              Some
                (Tezos.transaction
                   transfer_param
                   0mutez
                   (get_contract_FA12_transfer token_address))
          | Fa2 (token_address, token_id) -> 
              Some
                (Tezos.transaction
                   [
                     {
                       from_ = from_addr;
                       txs =
                         [
                           {
                             to_ = to_addr;
                             token_id = token_id;
                             amount = token_amount;
                           };
                         ];
                     };
                   ]
                   0mutez
                   (get_contract_FA2_transfer token_address))
          | Xtz -> 
              if to_addr = Tezos.self_address then
                  None
              else
                  Some (Tezos.transaction () (natural_to_mutez token_amount) (get_contract_tez_to to_addr)) 


[@inline]
let a_or_b_is_SMAK (store : storage) : a_or_b option =
  if
    check_tokens_equal
      store.token_type_smak
      store.token_type_a
  then Some A
  else if
    check_tokens_equal
      store.token_type_smak
      store.token_type_b
  then Some B
  else None

[@inline]
let burn_smak (store : storage) (from : address) (token_amount : nat) :
    operation option =
  make_transfer
    store.token_type_smak
    from
    ("tz1Ke2h7sDdakHJQh8WX4Z372du1KChsksyU" : address)
    token_amount

[@inline]
let mint_or_burn (store : storage) (target : address) (quantity : int) :
    operation option =
  if quantity = 0 then 
    None
  else
    let lqt_admin : mint_or_burn contract =
      let lqt_address =
        match store.lqt_address with
        | None -> (failwith error_LQT_ADDRESS_IS_NOT_SET : address)
        | Some lqt_address -> lqt_address
      in
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
let opt_to_op_list (opt_list : (operation option) list) : operation list =
    let ops = ([] : operation list) in
    List.fold (fun (l, op : operation list * operation option) ->
                match op with
                | None -> l
                | Some o -> o :: l) opt_list ops

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
    (* since x >0 and y > 0, x + y > x - y and therefore (x + y)^7 > (x - y)^7 and (x + y^7 - (x - y)^7 > 0 *)
    (abs (plus_8 - minus_8), 8n * (abs (minus_7 + plus_7)))

type newton_param =  {x : nat ; y : nat ; dx : nat ; dy : nat ; u : nat ; n : int}
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
    ((in_total * 10000n) + token_in) 
    | Flat ->
    (flat in_total out_total token_in / 10000n) in
  b_out

[@inline]
let compute_out_amount_when_A_or_B_is_SMAK (a_to_b : bool) (aorb_smak : a_or_b) (token_in : nat) (in_total : nat) (out_total : nat) (curve : curve_type) : (nat * nat * nat) =
  let reduce = 
    match curve with
    | Flat -> 9990n
    | Product -> 9972n in
  let total_fees = abs (10000n - reduce) in
  match aorb_smak with
  | A ->
    if a_to_b
    then
      let b_out = compute_out_amount (token_in * reduce) in_total out_total curve in
      (b_out, ((total_fees * token_in) / 10000n), 0n)
    else
      let bought_pre =
        match curve with
        | Flat -> flat (in_total * reduce) out_total token_in / 10000n
        | Product -> 
          (token_in * out_total) / (in_total + token_in) in
      (((reduce * bought_pre) / 10000n), ((total_fees * bought_pre) / 10000n), 0n)
  | B ->
    if a_to_b
    then
      let bought_pre = 
        match curve with
        | Flat -> flat (in_total * reduce) out_total token_in / 10000n
        | Product -> 
          (token_in * out_total) / (in_total + token_in) in
      (((reduce * bought_pre) / 10000n), 0n, ((total_fees * bought_pre) / 10000n))
    else
      (let b_out = compute_out_amount (token_in * reduce) in_total out_total curve in
       (b_out, 0n, ((total_fees * token_in) / 10000n)))

(** Create operations to either withdraw (when the token is not the
   SMAK token) or burn (when the token is the SMAK token) the
   tokens. *)
let withdraw_or_burn_fees (store : storage) (reserve_fee_to_burn_A : nat)
    (reserve_fee_to_burn_B : nat) : (operation option) list =
  let withdraw_or_burn_op_A =
    (* if A is SMAK, burn them *)
    if
      check_tokens_equal
        store.token_type_a
        store.token_type_smak
    then
      (* check if not 0 *)
      burn_smak store Tezos.self_address reserve_fee_to_burn_A
    else
      (* otherwise transfer them to reserve *)
      make_transfer
        store.token_type_a
        Tezos.self_address
        store.reserve
        reserve_fee_to_burn_A
  in
  let withdraw_or_burn_op_B =
    (* if B is SMAK, burn them *)
    if
      check_tokens_equal
        store.token_type_b
        store.token_type_smak
    then burn_smak store Tezos.self_address reserve_fee_to_burn_B
    else
      (* otherwise transfer them to reserve *)
      make_transfer
        store.token_type_b
        Tezos.self_address
        store.reserve
        reserve_fee_to_burn_B
  in
    [withdraw_or_burn_op_A; withdraw_or_burn_op_B]

let compute_fees (store : storage) (amount_in_a : nat) (amount_in_b : nat)
    (feeSMAK_A : nat) (feeSMAK_B : nat) : amounts_and_fees =
  match a_or_b_is_SMAK store with
  | Some _ ->
      (* A or B is SMAK: no Uniswap-like adjustments to make *)
      {
        amount_in_A = amount_in_a;
        amount_in_B = amount_in_b;
        reserve_fee_in_A = feeSMAK_A;
        reserve_fee_in_B = feeSMAK_B;
      }
  | None -> (
      (* Neither A nor B is the SMAK token: See Uniswapv2 whitepaper
         or working document to explain these computations *)
      let k1 = store.last_k in
      let k2 = amount_in_a * amount_in_b in
      let sqr1 = sqrt k1 in
      let sqr2 = sqrt k2 in
      match is_a_nat (sqr2 - sqr1) with
      | None ->
          (failwith error_K2_SHOULD_BE_GREATER_THAN_K1 : amounts_and_fees)
      | Some sq2minussq1 ->
          let sm =
            (* stillborn, protocol-fee, Uniswap-minted shares  *)
            sq2minussq1 * store.lqt_total / (ceildiv (25n * sqr2) 3n + sqr1)
          in
          (* new reserve fee to "burn" in A *)
          let arl = sm * amount_in_a / (store.lqt_total + sm) in
          (* new reserve fee to "burn" in B *)
          let brl = sm * amount_in_b / (store.lqt_total + sm) in
          let new_token_pool_a =
            match is_nat (amount_in_a - arl) with
            | None -> (failwith error_A_PROTOCOL_FEE_IS_TOO_BIG : nat)
            | Some new_token_pool_a -> new_token_pool_a
          in
          let new_token_pool_b =
            match is_nat (amount_in_b - brl) with
            | None -> (failwith error_B_PROTOCOL_FEE_IS_TOO_BIG : nat)
            | Some new_token_pool_b -> new_token_pool_b
          in
          {
            amount_in_A = new_token_pool_a;
            amount_in_B = new_token_pool_b;
            reserve_fee_in_A = arl;
            reserve_fee_in_B = brl;
          })


[@inline]
let get_contract_FA2_balance_of (token_address : address) : balance_of_param contract =
  match (Tezos.get_entrypoint_opt "%balance_of" token_address : balance_of_param
             contract
             option)
  with
  | None ->
    (failwith error_INVALID_FA2_TOKEN_CONTRACT_MISSING_BALANCE_OF : balance_of_param
         contract)
  | Some contract -> contract


[@inline]
let get_contract_FA12_get_balance (token_address : address) : get_balance_fa12 contract =
  match (Tezos.get_entrypoint_opt "%getBalance" token_address : get_balance_fa12 contract option)
  with
  | None ->
    (failwith error_INVALID_FA12_TOKEN_CONTRACT_MISSING_GETBALANCE : 
       get_balance_fa12 contract)
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