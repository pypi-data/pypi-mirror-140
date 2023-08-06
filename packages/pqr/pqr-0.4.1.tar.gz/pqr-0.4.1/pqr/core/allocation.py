"""Module, containing functions to allocate picks and some subsequent steps
(leveraging and allocating cash).
"""

from __future__ import annotations

__all__ = [
    "equal_weights",
    "normalized_weights",
    "scale",
    "allocate_cash",
]

import numpy as np
import pandas as pd

from pqr.utils import align


def equal_weights(picks: pd.DataFrame) -> pd.DataFrame:
    """Weighs picks equally.

    Different normalizers are used for long and short positions.

    Parameters
    ----------
    picks : pd.DataFrame
        Matrix, consists of 1/0/-1, indicating longs, shorts and no position.

    Returns
    -------
    pd.DataFrame
        Matrix with the same rows and columns, but indicators are replaced to
        equal weights.
    """

    picks_array = picks.to_numpy()
    longs, shorts = picks_array > 0, picks_array < 0
    return pd.DataFrame(
        _normalize(longs) - _normalize(shorts),
        index=picks.index.copy(),
        columns=picks.columns.copy()
    )


def normalized_weights(
        picks: pd.DataFrame,
        base_weights: pd.DataFrame,
) -> pd.DataFrame:
    """Weighs picks, based on `base_weights`.

    Different normalizers are used for long and short positions.

    Parameters
    ----------
    picks : pd.DataFrame
        Matrix, consists of 1/0/-1, indicating longs, shorts and no position.
    base_weights : pd.DataFrame
        Matrix with base weights (e.g. market capitalization).

    Returns
    -------
    pd.DataFrame
        Matrix with indicators replaced to normalized weights.
    """

    picks, base_weights = align(picks, base_weights)
    holdings_array, w_array = picks.to_numpy(), base_weights.to_numpy()
    longs, shorts = holdings_array > 0, holdings_array < 0
    return pd.DataFrame(
        _normalize(longs * w_array) - _normalize(shorts * w_array),
        index=picks.index.copy(),
        columns=picks.columns.copy(),
    )


def _normalize(raw_weights: np.ndarray) -> np.ndarray:
    normalizing_coef = np.nansum(
        raw_weights,
        axis=1, keepdims=True, dtype=float,
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.nan_to_num(
            raw_weights / normalizing_coef,
            nan=0, neginf=0, posinf=0,
        )


def scale(
        holdings: pd.DataFrame,
        base_leverage: pd.DataFrame,
        min_leverage: float = -np.inf,
        max_leverage: float = np.inf,
) -> pd.DataFrame:
    """Scales `holdings`, based on given `base_leverage`.

    Simply multiplies `holdings` and `base_leverage`. Then fixes leverage to
    not exceed min and max leverage bounds (if given).

    Parameters
    ----------
    holdings : pd.DataFrame
        Matrix of weights of positions.
    base_leverage : pd.DataFrame
        Matrix with base leverage (e.g. volatility).
    min_leverage : float
        Minimum allowed total leverage in a period.
    max_leverage : float
        Maximum allowed total leverage in a period.

    Returns
    -------
    pd.DataFrame
        Matrix with scaled weights.
    """

    holdings, base_leverage = align(holdings, base_leverage)

    leveraged_w = holdings.to_numpy() * base_leverage.to_numpy()
    total_leverage = np.nansum(leveraged_w, axis=1, keepdims=True)

    with np.errstate(divide="ignore", invalid="ignore"):
        exceed_min = total_leverage < min_leverage
        under_min = (np.where(exceed_min, leveraged_w, 0) /
                     np.where(exceed_min, total_leverage, 1)) * min_leverage

        exceed_max = total_leverage > max_leverage
        above_max = (np.where(exceed_max, leveraged_w, 0) /
                     np.where(exceed_max, total_leverage, 1)) * max_leverage

    return pd.DataFrame(
        np.where(~(exceed_min | exceed_max), leveraged_w, 0) +
        under_min + above_max,
        index=holdings.index.copy(),
        columns=holdings.columns.copy(),
    )


def allocate_cash(
        holdings: pd.DataFrame,
        prices: pd.DataFrame,
        capital: float = 1_000_000.0,
        fee: float = 0.0,
) -> pd.DataFrame:
    """Simulates the process of allocating real money.

    Can be used to estimate more realistic portfolio, which is imperfect and
    has some cash residuals and meets the commission.

    Parameters
    ----------
    holdings : pd.DataFrame
        Matrix of weights of positions.
    prices : pd.DataFrame
        Matrix with obtainable prices to make deals.
    capital : float
        Initial balance.
    fee : float
        Relative commission rate.

    Returns
    -------
    pd.DataFrame
        Matrix with relative positions, initially allocated with money. Also
        has a column, named "cash_residuals", where stored relative amount of
        not allocated money.
    """

    prices, weights = align(prices, holdings)
    prices_arr = prices.to_numpy()
    weights_arr = weights.to_numpy()

    allocation = np.zeros_like(weights_arr, dtype=int)
    cash = np.ones(allocation.shape[0]) * capital
    balance = cash.copy()

    for i in range(len(allocation)):
        w, p = weights_arr[i], prices_arr[i]
        prev_alloc = allocation[max(0, i - 1)]
        prev_cash = cash[max(0, i - 1)]

        allocation[i], cash[i], balance[i] = _allocation_step(
            w, p, prev_alloc, prev_cash, fee)

    positions_in_cash = np.nan_to_num(
        np.insert(
            allocation * prices_arr,
            obj=0, axis=1, values=cash
        ),
        nan=0, neginf=0, posinf=0
    )

    return pd.DataFrame(
        positions_in_cash / balance[:, np.newaxis],
        index=weights.index.copy(),
        columns=["cash_residuals"] + list(weights.columns.copy())
    )


def _allocation_step(
        weights: np.ndarray,
        prices: np.ndarray,
        prev_alloc: np.ndarray,
        prev_cash: float,
        fee: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    balance = prev_cash + np.nansum(prev_alloc * prices)
    allocation_delta = _close_positions(weights, prev_alloc)
    commission = _accrue_commission(allocation_delta, prices, fee)

    to_rebalance = (allocation_delta == 0) & (prev_alloc != 0) & (weights != 0)
    allocation_delta[to_rebalance] = _rebalance_positions(
        weights[to_rebalance],
        prices[to_rebalance],
        prev_alloc[to_rebalance],
        balance - commission,
        fee
    )
    commission = _accrue_commission(allocation_delta, prices, fee)

    to_open = (allocation_delta == 0) & (prev_alloc == 0) & (weights != 0)
    allocation_delta[to_open] = _open_positions(
        weights[to_open],
        prices[to_open],
        prev_alloc[to_open],
        balance - commission,
        fee
    )
    commission = _accrue_commission(allocation_delta, prices, fee)

    cash_delta = -(allocation_delta * prices)
    allocation_delta = prev_alloc + allocation_delta
    cash = prev_cash + np.nansum(cash_delta) - commission

    return allocation_delta, cash, balance


def _close_positions(
        weights: np.ndarray,
        prev_alloc: np.ndarray,
) -> np.ndarray:
    return -prev_alloc * (weights == 0)


def _rebalance_positions(
        weights: np.ndarray,
        prices: np.ndarray,
        prev_alloc: np.ndarray,
        balance: float,
        fee: float,
) -> np.ndarray:
    ideal_alloc = balance * weights / prices
    allocation = (ideal_alloc - prev_alloc)
    allocation[allocation > 0] *= 1 - fee
    allocation[allocation < 0] *= 1 + fee

    buy, sell = allocation > 0, allocation < 0
    long, short = prev_alloc > 0, prev_alloc < 0
    buy_more, sell_some = buy & long, sell & long  # rebalance longs
    sell_more, buy_some = sell & short, buy & short  # rebalance shorts

    allocation[buy_more | sell_more] = np.trunc(
        allocation[buy_more | sell_more])
    allocation[sell_some] = np.floor(allocation[sell_some])
    allocation[buy_some] = np.ceil(allocation[buy_some])

    return np.nan_to_num(allocation, nan=0)


def _open_positions(
        weights: np.ndarray,
        prices: np.ndarray,
        prev_alloc: np.ndarray,
        balance: float,
        fee: float,
) -> np.ndarray:
    ideal_alloc = balance * weights / prices
    allocation = (ideal_alloc - prev_alloc) * (1 - fee)
    allocation[allocation > 0] *= 1 - fee
    allocation[allocation < 0] *= 1 + fee

    return np.nan_to_num(np.trunc(allocation), nan=0)


def _accrue_commission(
        allocation: np.ndarray,
        prices: np.ndarray,
        fee: float,
) -> np.ndarray:
    return np.nansum(np.abs(allocation * prices)) * fee
