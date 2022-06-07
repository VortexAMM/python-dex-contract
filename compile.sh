alias ligo="docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.41.0"

ligo compile contract liquidity_token/lqt_fa12.mligo --protocol ithaca > michelson/lqt_fa12.tz
ligo compile contract sink/sink.mligo --protocol ithaca > michelson/sink.tz
ligo compile contract dex/dex.mligo --protocol ithaca > michelson/dex.tz
ligo compile contract factory/factory.mligo --protocol ithaca > michelson/factory.tz
ligo compile contract multisig/multisig.mligo --protocol ithaca > michelson/multisig.tz