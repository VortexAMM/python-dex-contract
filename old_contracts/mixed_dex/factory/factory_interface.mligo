#if !FACTORY_INTERFACE
#define FACTORY_INTERFACE

type create_dex_func = (operation * address)

type allowance_key =
  [@layout:comb]
  { owner : address;
    spender : address }

type tokens = (address, nat) big_map
type allowances = (allowance_key, nat) big_map

type investment_direction =
  | Add
  | Remove

type investment_delta = {
  xtz : tez ;
  token : nat ;
  direction : investment_direction ;
}

//type curve_type =
//| Flat
//| Product

type dex_storage =
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

#if FA2
type token_identifier = address * nat
#else
type token_identifier = address
#endif

type token_metadata_entry = {
  token_id: nat;
  token_info: (string, bytes) map;
}
type storage = {
  swaps: (nat, address) big_map;
  token_to_swaps: (token_identifier, address) big_map;
  counter: nat;
  empty_history: (string, nat) big_map;
  empty_user_investments: (address, investment_delta) big_map;
  empty_tokens: (address, nat) big_map;
  empty_allowances: (allowance_key, nat) big_map;
  default_reserve: address;
  default_token_metadata : (nat, token_metadata_entry) big_map;
  default_metadata: (string, bytes) big_map;
}
type result = operation list * storage

type lp_token_storage =
  [@layout:comb]
  { tokens : tokens;
    allowances : allowances;
    admin : address;
    total_supply : nat;
    metadata : (string, bytes) big_map;
    token_metadata : (nat, token_metadata_entry) big_map;
  }

type transfer =
  [@layout:comb]
  { [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat }

type set_lqt_address_param = {
  dex_address: address;
  lqt_address: address;
}

type launch_exchange_mixed_param = {
    token_address: address;
#if FA2
    token_id: nat;
#endif
    token_amount: nat;
}

type txs_item =
  [@layout:comb]
  {
    to_: address;
    token_id: nat;
    amount: nat;
}


type transfer_fa2_item =
  [@layout:comb]
  {
    from_: address;
    txs: txs_item list;
  }
type transfer_fa2 = transfer_fa2_item list

type launch_exchange_param =
[@layout:comb]
{
  token_address : address;
#if FA2
  token_id : nat;
#endif
  token_amount : nat;
}

type param =
    | LaunchExchangeMixed of launch_exchange_param
    | SetLqtAddress of set_lqt_address_param



#endif