#if !DEX_FUNCTIONS
#define DEX_FUNCTIONS

[@inline]
let mutez_to_natural (a: tez) : nat =  a / 1mutez

[@inline]
let natural_to_mutez (a: nat): tez = a * 1mutez

[@inline]
let is_a_nat (i : int) : nat option = Michelson.is_nat i

let ceildiv (numerator : nat) (denominator : nat) : nat =
    match (ediv numerator denominator) with
        | None   -> (failwith("DIV by 0") : nat)
        | Some v ->  let (q, r) = v in if r = 0n then q else q + 1n



[@inline]
let mint_or_burn (store : storage) (target : address) (quantity : int) : operation =
    let lqt_admin : mint_or_burn contract =
    match (Tezos.get_entrypoint_opt "%mintOrBurn" store.lqt_address :  mint_or_burn contract option) with
    | None -> (failwith error_LQT_CONTRACT_MUST_HAVE_A_MINT_OR_BURN_ENTRYPOINT : mint_or_burn contract)
    | Some contract -> contract in
    Tezos.transaction {quantity = quantity ; target = target} 0mutez lqt_admin

[@inline]
let token_transfer (store : storage) (from : address) (to_ : address) (token_amount : nat) : operation =
    let token_contract: token_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" store.token_address : token_contract_transfer contract option) with
    | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : token_contract_transfer contract)
    | Some contract -> contract in
#if FA2
    Tezos.transaction [(from, [(to_, (store.token_id, token_amount))])] 0mutez token_contract
#else
    Tezos.transaction (from, (to_, token_amount)) 0mutez token_contract
#endif

[@inline]
let xtz_transfer (to_ : address) (amount_ : tez) : operation =
    let to_contract : unit contract =
    match (Tezos.get_contract_opt to_ : unit contract option) with
    | None -> (failwith error_INVALID_TO_ADDRESS : unit contract)
    | Some c -> c in
    Tezos.transaction () amount_ to_contract

let update_xtz_volume (xtz_amount : tez) (history : (string, nat) big_map) =
  let current_xtz_volume = match Big_map.find_opt "xtz_volume" history with
    | Some v -> v
    | None -> 0n
  in
  Big_map.update "xtz_volume" (Some (current_xtz_volume + (mutez_to_natural xtz_amount))) history

type poly_param =
{
    x : nat;
    n : nat;
}

//let rec poly (param : poly_param) : nat = 
//    let { x = x; n = n} = param in
//    if n = 0n then x
//    else
//        let raised_x = x * x in
//        let new_n = n / 2n in
//        poly {x = raised_x; n =  new_n}
//
//let flat_curve (x : nat) (y : nat) : (nat * nat) =
//    let u = abs ((poly {x = (x + y); n = 8n}) - (poly {x = (abs (x - y)); n = 8n})) in
//    let du_dy = 
//        if abs(x - y) = 0n then 
//            8n * (poly {x = (x + y); n = 8n}) / (x + y)
//        else
//            8n * ((poly { x = (x + y); n = 8n}) / (x + y) + (poly {x = (abs(x - y)); n = 8n}) / abs(x - y)) in
//    u, du_dy
//
//type newton_param =  {x : nat ; y : nat ; dx : nat ; dy : nat ; u : nat ; n : int}
//
//let rec newton (p : newton_param) : nat =
//    if p.n = 0 then
//        p.dy
//    else
//        let new_u, new_du_dy = flat_curve (p.x + p.dx) (abs (p.y - p.dy)) in //util returns calculation of u and the derivative with respect to y
//        (* new_u - p.u > 0 because dy remains an underestimate *)
//        let dy = p.dy + abs ((new_u - p.u) / new_du_dy) in
//        (* dy is an underestimate because we start at 0 and the utility curve is convex *)
//        newton {p with dy = dy ; n = p.n - 1}

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
let rec newton (p : newton_param) : nat =
    if p.n = 0 then
        p.dy
    else
        let new_u, new_du_dy = util (p.x + p.dx) (abs (p.y - p.dy)) in //util returns calculation of u and the derivative with respect to y
        (* new_u - p.u > 0 because dy remains an underestimate *)
        let dy = p.dy + abs ((new_u - p.u) / new_du_dy) in
        (* dy is an underestimate because we start at 0 and the utility curve is convex *)
        newton {p with dy = dy ; n = p.n - 1}


let tokens_bought (pool_a : nat) (pool_b : nat) (diff_a : nat) : nat =
    let x = pool_a in
    let y = pool_b in
    let u, _ = util x y in
    (newton {x = x; y = y ; dx = diff_a ; dy = 0n ; u = u ; n = 5})

#endif