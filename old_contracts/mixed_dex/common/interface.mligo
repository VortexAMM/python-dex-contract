#if !COMMON_INTERFACE
#define COMMON_INTERFACE

(* token entrypoint types *)

type token_id = nat

type transfer_destination =
[@layout:comb]
{
  to_ : address;
  token_id : token_id;
  amount : nat;
}

type fa2_transfer =
[@layout:comb]
{
  from_ : address;
  txs : transfer_destination list;
}

type fa12_transfer = 
[@layout:comb]
{
  [@annot:from]address_from : address;
  [@annot:to]address_to : address;
  value : nat;
}

type entrypoint_signature =
{
    name : string;
    params : bytes;
    source_contract : address;
}
type call_param =
[@layout:comb]
{
    entrypoint_signature : entrypoint_signature;
    callback : unit -> operation list;
}

//type launch_exchange_t2t_param =
//[@layout:comb]
//{
//    address_a: address ;
//    id_a: fa_token ;
//    amount_a: nat ;
//    address_b: address ;
//    id_b: fa_token ;
//    amount_b: nat;
//    curve : curve_type;
//}

#endif