"""Password hashing and credential validation (app/auth.py).

The account flows in test_accounts.py exercised these through HTTP; nothing
tested the primitives directly, including the parts that only fire on malformed
stored data.
"""
import pytest

from app import auth


# --- hashing --------------------------------------------------------------
def test_hash_is_self_describing_and_salted():
    a = auth.hash_password("password123")
    b = auth.hash_password("password123")
    assert a.startswith("scrypt$")
    assert len(a.split("$")) == 6
    # A fresh salt per call, so identical passwords never share a hash.
    assert a != b
    assert auth.verify_password("password123", a)
    assert auth.verify_password("password123", b)


def test_verify_rejects_the_wrong_password():
    encoded = auth.hash_password("password123")
    assert not auth.verify_password("password124", encoded)
    assert not auth.verify_password("", encoded)


@pytest.mark.parametrize("encoded", [
    None, "", "not-a-hash", "scrypt$bad", "bcrypt$1$2$3$aa$bb",
    "scrypt$16384$8$1$nothex$nothex", "scrypt$x$8$1$aa$bb",
])
def test_verify_is_false_on_anything_malformed(encoded):
    # A guest row has password_hash NULL; a corrupted row must not raise either.
    assert auth.verify_password("password123", encoded) is False


def test_password_is_not_recoverable_from_the_hash():
    assert "password123" not in auth.hash_password("password123")


# --- usernames ------------------------------------------------------------
def test_username_is_normalized_lowercase():
    assert auth.normalize_username("  ArMaN  ") == "arman"
    assert auth.normalize_username("") == ""
    assert auth.validate_username("  ArMaN  ") == "arman"


@pytest.mark.parametrize("raw", ["abc", "a.b_c-d", "a1", None])
def test_username_length_and_charset(raw):
    if raw in (None, "a1"):  # too short / not a string
        with pytest.raises(ValueError):
            auth.validate_username(raw)
    else:
        assert auth.validate_username(raw) == raw


@pytest.mark.parametrize("raw", [
    "ab", "a" * 33, "has space", "hasUPPER!", "emoji🙂", "semi;colon", "",
])
def test_invalid_usernames_are_refused(raw):
    with pytest.raises(ValueError):
        auth.validate_username(raw)


def test_uppercase_username_normalizes_rather_than_failing():
    # The charset regex only allows lowercase, so this passes *because*
    # validate_username normalizes first. That ordering is the whole point.
    assert auth.validate_username("ArMaN99") == "arman99"


# --- email ----------------------------------------------------------------
def test_email_is_optional():
    for blank in (None, "", "   "):
        assert auth.normalize_email(blank) is None
        assert auth.validate_email(blank) is None


def test_email_is_normalized_lowercase():
    assert auth.validate_email("  Me@Example.COM ") == "me@example.com"


@pytest.mark.parametrize("raw", ["nope", "a@b", "@example.com", "a b@c.com",
                                "two@at@example.com"])
def test_invalid_emails_are_refused(raw):
    with pytest.raises(ValueError):
        auth.validate_email(raw)


# --- password policy ------------------------------------------------------
def test_password_minimum_length():
    assert auth.validate_password("a" * auth.MIN_PASSWORD_LEN)
    with pytest.raises(ValueError):
        auth.validate_password("a" * (auth.MIN_PASSWORD_LEN - 1))
    with pytest.raises(ValueError):
        auth.validate_password("")
