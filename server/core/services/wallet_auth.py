"""EIP-191 wallet authentication helpers (any EIP-1193 browser wallet)."""

from __future__ import annotations

import re
import secrets

from django.core.cache import cache
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address

from core.models import TrakUser

WALLET_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
NONCE_TTL_SECONDS = 300
APP_NAME = "Haztrak"


class WalletAuthError(Exception):
    """Raised when wallet authentication fails."""


def normalize_address(address: str) -> str:
    """Validate and checksum-normalize a wallet address."""
    if not address or not WALLET_ADDRESS_RE.match(address):
        msg = "Invalid wallet address."
        raise WalletAuthError(msg)
    return to_checksum_address(address)


def _nonce_cache_key(address: str) -> str:
    return f"wallet_auth_nonce:{address.lower()}"


def build_sign_in_message(*, address: str, nonce: str) -> str:
    """Build the plaintext message the wallet must sign."""
    return (
        f"{APP_NAME} wants you to sign in with your wallet.\n\n"
        f"Address: {address}\n"
        f"Nonce: {nonce}\n"
        "This request will not trigger a blockchain transaction or cost any gas."
    )


def issue_wallet_nonce(address: str) -> dict[str, str]:
    """Create a short-lived nonce and sign-in message for an address."""
    checksum = normalize_address(address)
    nonce = secrets.token_hex(16)
    cache.set(_nonce_cache_key(checksum), nonce, timeout=NONCE_TTL_SECONDS)
    message = build_sign_in_message(address=checksum, nonce=nonce)
    return {"address": checksum, "nonce": nonce, "message": message}


def verify_wallet_signature(*, address: str, signature: str, message: str) -> str:
    """Verify an EIP-191 personal_sign signature and consume the nonce."""
    checksum = normalize_address(address)
    expected_nonce = cache.get(_nonce_cache_key(checksum))
    if not expected_nonce:
        msg = "Sign-in challenge expired. Request a new one."
        raise WalletAuthError(msg)

    expected_message = build_sign_in_message(address=checksum, nonce=expected_nonce)
    if message.strip() != expected_message.strip():
        msg = "Signed message does not match the issued challenge."
        raise WalletAuthError(msg)

    try:
        recovered = Account.recover_message(encode_defunct(text=message), signature=signature)
    except Exception as exc:  # noqa: BLE001 - eth_account raises varied errors
        msg = "Invalid wallet signature."
        raise WalletAuthError(msg) from exc

    if recovered.lower() != checksum.lower():
        msg = "Signature does not match wallet address."
        raise WalletAuthError(msg)

    cache.delete(_nonce_cache_key(checksum))
    return checksum


def get_or_create_wallet_user(address: str) -> tuple[TrakUser, bool]:
    """Find or create a Haztrak user bound to a wallet address."""
    from profile.services import get_or_create_profile

    checksum = normalize_address(address)
    user = TrakUser.objects.filter(wallet_address__iexact=checksum).first()
    if user is not None:
        return user, False

    username = checksum.lower()
    if TrakUser.objects.filter(username__iexact=username).exists():
        username = f"wallet_{checksum[2:10].lower()}"

    user = TrakUser.objects.create_user(
        username=username,
        email="",
        password=None,
        wallet_address=checksum,
    )
    user.set_unusable_password()
    user.save(update_fields=["password"])
    get_or_create_profile(username=user.username)
    return user, True
