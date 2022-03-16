alias ligo="docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.37.0"

# ligo compile contract tokens/fa12.mligo --protocol hangzhou > michelson/fa12.tz
# ligo compile contract tokens/nft/nft.mligo --protocol hangzhou > michelson/fa2.tz
ligo compile contract liquidity_token/lqt_fa12.mligo --protocol hangzhou > michelson/lqt_fa12.tz
ligo compile contract sink/sink.mligo --protocol hangzhou > michelson/sink.tz
ligo compile contract dex/dex.mligo --protocol hangzhou > michelson/dex.tz
ligo compile contract baker_rewards/baker_rewards.mligo --protocol hangzhou > michelson/baker_rewards.tz
ligo compile contract factory/factory.mligo --protocol hangzhou > michelson/factory.tz