#include "../common/interface.mligo"

type approve_param = (address * nat)

type operator_param =
[@layout:comb]
{
  owner: address ;
  operator: address ;
  token_id: nat;
}

type operator_update =
[@layout:comb] 
| Add_operator of operator_param 
| Remove_operator of operator_param 

type claim_param =
[@layout:comb]
{
  tokens : token_type list;
  deadline : timestamp;
  reward_to : address;
}

type add_exchange_param = sink_add_exchange_param


type sink_deposit_param = sink_deposit_params

type get_address = address * bool

type storage = sink_storage

type return = (operation list * storage)

type parameter =
| Deposit of sink_deposit_param
| Claim of claim_param
| UpdateClaimLimit of nat
| AddExchange of add_exchange_param