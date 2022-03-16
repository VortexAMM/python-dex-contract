#if !DEX_INTERFACE
#define DEX_INTERFACE

type add_liquidity =
  [@layout:comb]
  { owner : address ;
    min_lqt_minted : nat ;
    max_tokens_deposited : nat ;
    deadline : timestamp ;
  }

type remove_liquidity =
  [@layout:comb]
  { [@annot:to] to_ : address ; // recipient of the liquidity redemption
    lqt_burned : nat ;  // amount of lqt owned by sender to burn
    min_xtz_withdrawn : tez ; // minimum amount of tez to withdraw
    min_tokens_withdrawn : nat ; // minimum amount of tokens to whitdw
    deadline : timestamp ; // the time before which the request must be completed
  }

type xtz_to_token =
  [@layout:comb]
  { [@annot:to] to_ : address ;
    min_tokens_bought : nat ;
    deadline : timestamp ;
  }

type token_to_xtz =
  [@layout:comb]
  { [@annot:to] to_ : address ;
    tokens_sold : nat ;
    min_xtz_bought : tez ;
    deadline : timestamp ;
  }

type set_baker =
  [@layout:comb]
  { baker : key_hash option ;
    freeze_baker : bool ;
  }

type token_to_token =
  [@layout:comb]
  { output_dexter_contract : address ;
    min_tokens_bought : nat ;
    [@annot:to] to_ : address ;
    tokens_sold : nat ;
    deadline : timestamp ;
  }

#if FA2
type update_token_pool_internal = ((address * nat) * nat) list
#else
type update_token_pool_internal = nat
#endif

type update_reserve = address

type entrypoint =
| UpdateReserve   of update_reserve
| AddLiquidity    of add_liquidity
| RemoveLiquidity of remove_liquidity
| XtzToToken      of xtz_to_token
| TokenToXtz      of token_to_xtz
| SetBaker        of set_baker
| SetManager      of address
| SetLqtAddress   of address
| Default         of unit
| UpdateTokenPool of unit
| UpdateTokenPoolInternal of update_token_pool_internal
| TokenToToken    of token_to_token

type investment_direction =
  | Add
  | Remove

type investment_delta = {
  xtz : tez ;
  token : nat ;
  direction : investment_direction ;
}

type storage =
  [@layout:comb]
  { token_pool : nat ;
    xtz_pool : tez ;
    lqt_total : nat ;
    self_is_updating_token_pool : bool ;
    freeze_baker : bool ;
    manager : address ;
    multisig : address;
    token_address : address ;
#if FA2
    token_id : nat ;
#endif
    lqt_address : address ;
    history : (string, nat) big_map ;
    user_investments : (address, investment_delta) big_map ;
    reserve : address ;
  }

type return = operation list * storage

#if FA2
// FA2
type token_id = nat
type token_contract_transfer = (address * (address * (token_id * nat)) list) list
type balance_of = ((address * token_id) list * ((((address * nat) * nat) list) contract))
#else
// FA1.2
type token_contract_transfer = address * (address * nat)
type get_balance = address * (nat contract)
#endif

// custom entrypoint for LQT FA1.2
type mint_or_burn =
  [@layout:comb]
  { quantity : int ;
    target : address }

#endif