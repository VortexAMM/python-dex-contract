alias ligo="docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.31.0"
# ligo compile contract mixed_dex/liquidity_token/lqt_fa12.mligo --protocol hangzhou > michelson/lqt_fa12.tz
ligo compile contract mixed_dex/dex/dex.mligo --protocol hangzhou > michelson/dex_fa12.tz
ligo compile contract mixed_dex/dex/dex_fa2.mligo --protocol hangzhou > michelson/dex_fa2.tz
ligo compile contract mixed_dex/factory/factory.mligo --protocol hangzhou > michelson/factory_fa12.tz
ligo compile contract mixed_dex/factory/factory_fa2.mligo --protocol hangzhou > michelson/factory_fa2.tz



# ligo compile contract mixed_dex/tokens/fa12.mligo --protocol hangzhou > michelson/fa12.tz
# ligo compile contract mixed_dex/tokens/nft/nft.mligo --protocol hangzhou > michelson/fa2.tz
# ligo compile contract mixed_dex/multisig/multisig.mligo --protocol hangzhou > michelson/multisig.tz
# ligo compile contract token_to_token/sink/sink.mligo --protocol hangzhou > michelson/sink.tz

# ligo compile contract mixed_dex/gen_factory/factory.mligo --protocol hangzhou > michelson/gen_factory.tz
# ligo compile contract mixed_dex/gen_dex/dex.mligo --protocol hangzhou > michelson/gen_dex.tz
# ligo compile contract token_to_token/dex/dex.mligo --protocol hangzhou > michelson/t2t_dex.tz
# ligo compile contract token_to_token/factory/factory.mligo --protocol hangzhou > michelson/t2t_factory.tz


