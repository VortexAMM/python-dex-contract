#if !COMMON_TYPES
#define COMMON_TYPES

type token = nat

type token_id = nat

type fa_token =
  | FA2 of token_id 
  | FA12 

type investment_direction =
  | ADD 
  | REMOVE 

type curve_type =
| Flat
| Product

type investment_delta =
  {
    token_invest_a: token ;
    token_invest_b: token ;
    direction: investment_direction }

type history_big_map = (string, nat) big_map

type user_investments_big_map = (address, investment_delta) big_map

type token_to_token = [@layout:comb]  {
to: address ;
  tokens_sold: token ;
  min_tokens_bought: token ;
  a_to_b: bool ;
  deadline: timestamp }

type dex_storage = 
[@layout:comb]
{
    token_pool_a: nat ;
    token_pool_b: nat ;
    lqt_total: nat ;
    self_is_updating_token_pool: bool ;
    manager: address ;
    token_address_a: address ;
    token_address_b: address ;
    token_address_smak: address ;
    lqt_address: address option ;
    token_id_a: fa_token ;
    token_id_b: fa_token ;
    token_id_smak: fa_token ;
    history: history_big_map ;
    user_investments: user_investments_big_map ;
    reserve: address ;
    last_k: token;
    curve : curve_type;
}

type sink_storage = 
[@layout:comb]
{
    token_smak : address;
    fa_token_smak : fa_token;
    factory_address : address;
}

type fa2_transfer_destination = [@layout:comb]  {
  to_: address ;
  token_id: nat ;
  amount: nat }

type fa2_transfer = [@layout:comb]  {
  from_: address ;
  txs: fa2_transfer_destination list }

type fa12_transfer = [@layout:comb]  {
  from: address ;
to: address ;
  value: nat }

type ledger = (address, nat) big_map

type operators_storage = ((address * address), unit) big_map

type token_metadata_storage = (nat, (nat * (string, bytes) map)) big_map

type fa2_storage =
  {
    admin: address ;
    pending_admin: address option ;
    paused: bool ;
    ledger: ledger ;
    operators: operators_storage ;
    token_metadata: token_metadata_storage ;
    supply: nat ;
    metadata: (string, bytes) big_map }

type balance_of_request = [@layout:comb]  {
  owner: address ;
  token_id: nat }

type balance_of_response = [@layout:comb]  {
  request: balance_of_request ;
  balance: nat }

type balance_of_param = [@layout:comb]  {
    requests: balance_of_request list ;
    callback: balance_of_response list contract }

type get_address_param =
  {
    a_addr: address ;
    a_id: fa_token ;
    b_addr: address ;
    b_id: fa_token ;
    direction: bool }

#endif