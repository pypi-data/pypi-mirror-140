from decimal import Decimal
from typing import Any, Literal

import pywaves as pw
from mb_std import Result, md


def send_waves(private_key: str, recipient: str, amount: int) -> Result[str]:
    try:
        acc = pw.Address(privateKey=private_key)
        res = acc.sendWaves(recipient=pw.Address(recipient), amount=amount)
        if "id" in res:
            return Result.new_ok(res["id"], res)
        return Result.new_error("unknown_response", res)
    except Exception as e:
        return Result(error=str(e))


def send_asset(private_key: str, recipient: str, asset_id: str, amount: int) -> Result[str]:
    try:
        acc = pw.Address(privateKey=private_key)
        res = acc.sendAsset(recipient=pw.Address(recipient), amount=amount, asset=pw.Asset(asset_id))
        if "id" in res:
            return Result.new_ok(res["id"], res)
        return Result.new_error("unknown_response", res)
    except Exception as e:
        return Result.new_error(str(e))


def place_order(
    private_key: str,
    side: Literal["sell", "buy"],
    pair: pw.AssetPair,
    amount: int,
    price: Decimal,
    matcher_fee: int | None = None,
) -> Result[str]:
    acc = pw.Address(privateKey=private_key)
    fee_calc = pw.WXFeeCalculator()
    res_str = ""
    try:
        if side == "sell":
            if matcher_fee is None:
                matcher_fee = fee_calc.calculatePercentSellingFee(pair.asset2.assetId, pair.asset1.assetId, amount)
            res = acc.sell(pair, amount, price, matcherFee=matcher_fee)
        else:
            # TODO: calc catcher_fee
            res = acc.buy(pair, amount, price, matcherFee=matcher_fee)
        res_str = str(res)
        if res == -1:
            return Result.new_error("-1")
        return Result.new_ok(res.orderId, md(res_str, matcher_fee))
    except Exception as e:
        return Result.new_error(str(e), md(res_str))


def get_ticker(pair: pw.AssetPair) -> Result[dict[str, Any]]:
    try:
        res = pair.ticker()["data"]
        return Result.new_ok(res)
    except Exception as e:
        return Result.new_error(str(e))


def get_orders(private_key: str, pair: pw.AssetPair) -> Result[list[dict]]:
    acc = pw.Address(privateKey=private_key)
    try:
        return Result.new_ok(acc.getOrderHistory(pair))
    except Exception as e:
        return Result.new_error(str(e))


def invoke_script(private_key: str, dapp_address: str, function_name: str, params: list, payments: list) -> Result[str]:
    try:
        acc = pw.Address(privateKey=private_key)
        res = acc.invokeScript(dapp_address, function_name, params, payments)
        if "id" in res:
            return Result.new_ok(res["id"], res)
        return Result.new_error("unknown_response", res)
    except Exception as e:
        return Result.new_error(str(e))
