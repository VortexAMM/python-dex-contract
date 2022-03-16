#if !COMMON_INTERFACE
#define COMMON_INTERFACE

type token_id = nat

type offer_id = (token_id * address * address) // (token_id, buyer, seller)

type swap_id = nat

type royalties_amount = nat

type royalties_info = 
[@layout:comb]
{
  issuer: address;
  royalties: royalties_amount;
}

type update_royalties_param = 
[@layout:comb] 
{ 
  token_id : token_id; 
  royalties : nat; 
} 

type update_fee_param =  nat 

type update_admin_param = address 

type update_proxy_param = 
[@layout:comb]
| Add_proxy of address
| Remove_proxy of address

type update_nft_address_param = address 

type update_royalties_address_param = address

type nft_mint_param = 
[@layout:comb] 
{ 
  token_id: nat; 
  token_metadata: (string, bytes) map; 
  amount_ : nat; 
} 

type royalties_mint_param = 
[@layout:comb]
{
  token_id : token_id;
  royalties : nat;
}

type offer_param_request = 
[@layout:comb] 
{ 
  token_id : token_id; 
  buyer : address; 
} 

type offer_param_callback = 
[@layout:comb] 
{ 
  offer_id : offer_id; 
  royalties_info : royalties_info; 
} 

type collect_param_callback = 
[@layout:comb]
{
  swap_id : swap_id;
  token_amount : nat; 
  royalties_info : royalties_info;
}

type collect_param_request = 
[@layout:comb] 
{ 
  swap_id : swap_id; 
  token_amount : nat;
} 

type swap_royalties_param = 
[@layout:comb] 
{ 
  token_id : token_id; 
  swap_id : swap_id; 
  token_amount : nat; 
} 

type collect_param_call = 
[@layout:comb] 
| CollectRequest of collect_param_request 
| CollectCallback of collect_param_callback 

type accept_offer_param_call = 
[@layout:comb] 
| OfferRequest of offer_param_request 
| OfferCallback of offer_param_callback 

type get_royalties_type = 
[@layout:comb]
| SwapRoyalties of swap_royalties_param 
| OfferRoyalties of offer_id 

type token_contract_transfer = (address * (address * (token_id * nat)) list) list 

#endif