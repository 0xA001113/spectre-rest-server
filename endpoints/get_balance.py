# encoding: utf-8
import os

from fastapi import Path, HTTPException
from pydantic import BaseModel

from server import app, spectred_client

SPECTRE_ADDRESS_PREFIX = os.getenv("ADDRESS_PREFIX", "spectre")


class BalanceResponse(BaseModel):
    address: str = (
        SPECTRE_ADDRESS_PREFIX
        + ":pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00"
    )
    balance: int = 38240000000


@app.get(
    "/addresses/{spectreAddress}/balance",
    response_model=BalanceResponse,
    tags=["Spectre addresses"],
)
async def get_balance_from_spectre_address(
    spectreAddress: str = Path(
        description="Spectre address as string e.g. "
        + SPECTRE_ADDRESS_PREFIX
        + ":pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
        regex=r"^" + SPECTRE_ADDRESS_PREFIX + r"\:[a-z0-9]{61,63}$",
    ),
):
    """
    Get the balance for a specified Spectre address.
    """
    resp = await spectred_client.request(
        "getBalanceByAddressRequest", params={"address": spectreAddress}
    )

    try:
        resp = resp["getBalanceByAddressResponse"]
    except KeyError:
        if (
            "getUtxosByAddressesResponse" in resp
            and "error" in resp["getUtxosByAddressesResponse"]
        ):
            raise HTTPException(
                status_code=400, detail=resp["getUtxosByAddressesResponse"]["error"]
            )
        else:
            raise

    try:
        balance = int(resp["balance"])

    # return 0 if address is ok, but no utxos there
    except KeyError:
        balance = 0

    return {"address": spectreAddress, "balance": balance}
