# pylint: disable=missing-docstring,no-self-use
import json
import os
import time

import pytest
from jwkest.jws import JWS, factory
from jwkest.jwt import JWT

from oicmsg.key_bundle import keybundle_from_local_file
from oicmsg.key_bundle import KeyBundle
from oicmsg.key_jar import build_keyjar
from oicmsg.key_jar import key_export
from oicmsg.key_jar import KeyJar

__author__ = 'Roland Hedberg'

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         "data/keys"))

RSAKEY = os.path.join(BASE_PATH, "cert.key")
RSA0 = os.path.join(BASE_PATH, "rsa.key")

JWK0 = {"keys": [
    {'kty': 'RSA', 'e': 'AQAB', 'kid': "abc",
     'n':
         'wf-wiusGhA-gleZYQAOPQlNUIucPiqXdPVyieDqQbXXOPBe3nuggtVzeq7pVFH1dZz4dY2Q2LA5DaegvP8kRvoSB_87ds3dy3Rfym_GUSc5'
          'B0l1TgEobcyaep8jguRoHto6GWHfCfKqoUYZq4N8vh4LLMQwLR6zi6Jtu82nB5k8'}
]}

JWK1 = {"keys": [
    {
        "n":
            "zkpUgEgXICI54blf6iWiD2RbMDCOO1jV0VSff1MFFnujM4othfMsad7H1kRo50YM5S_X9TdvrpdOfpz5aBaKFhT6Ziv0nhtcekq1eRl8"
             "mjBlvGKCE5XGk-0LFSDwvqgkJoFYInq7bu0a4JEzKs5AyJY75YlGh879k1Uu2Sv3ZZOunfV1O1Orta-NvS-aG_jN5cstVbCGWE20H0vF"
             "VrJKNx0Zf-u-aA-syM4uX7wdWgQ"
            "-owoEMHge0GmGgzso2lwOYf_4znanLwEuO3p5aabEaFoKNR4K6GjQcjBcYmDEE4CtfRU9AEmhcD1k"
             "leiTB9TjPWkgDmT9MXsGxBHf3AKT5w",
        "e": "AQAB", "kty": "RSA", "kid": "rsa1"},
    {
        "k":
            "YTEyZjBlMDgxMGI4YWU4Y2JjZDFiYTFlZTBjYzljNDU3YWM0ZWNiNzhmNmFlYTNkNTY0NzMzYjE",
        "kty": "oct"},
]}

JWK2 = {
    "keys": [
        {
            "e": "AQAB",
            "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0/",
            "kid": "kriMPdmBvx68skT8-mPAB3BseeA",
            "kty": "RSA",
            "n":
                "kSCWg6q9iYxvJE2NIhSyOiKvqoWCO2GFipgH0sTSAs5FalHQosk9ZNTztX0ywS_AHsBeQPqYygfYVJL6_EgzVuwRk5txr9e3n1um"
                 "l94fLyq_AXbwo9yAduf4dCHTP8CWR1dnDR"
                "-Qnz_4PYlWVEuuHHONOw_blbfdMjhY"
                "-C_BYM2E3pRxbohBb3x__CfueV7ddz2LYiH3"
                 "wjz0QS_7kjPiNCsXcNyKQEOTkbHFi3mu0u13SQwNddhcynd_GTgWN8A"
                "-6SN1r4hzpjFKFLbZnBt77ACSiYx-IHK4Mp-NaVEi5wQt"
                 "SsjQtI--XsokxRDqYLwus1I1SihgbV_STTg5enufuw",
            "use": "sig",
            "x5c": [
                "MIIDPjCCAiqgAwIBAgIQsRiM0jheFZhKk49YD0SK1TAJBgUrDgMCHQUAMC0xKzApBgNVBAMTImFjY291bnRzLmFjY2Vzc2NvbnRyb"
                "2wud2luZG93cy5uZXQwHhcNMTQwMTAxMDcwMDAwWhcNMTYwMTAxMDcwMDAwWjAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb2"
                "50cm9sLndpbmRvd3MubmV0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkSCWg6q9iYxvJE2NIhSyOiKvqoWCO2GFipg"
                "H0sTSAs5FalHQosk9ZNTztX0ywS/AHsBeQPqYygfYVJL6"
                "/EgzVuwRk5txr9e3n1uml94fLyq/AXbwo9yAduf4dCHTP8CWR1dnDR+Q"
                "nz/4PYlWVEuuHHONOw/blbfdMjhY+C/BYM2E3pRxbohBb3x"
                "//CfueV7ddz2LYiH3wjz0QS/7kjPiNCsXcNyKQEOTkbHFi3mu0u13S"
                "QwNddhcynd/GTgWN8A+6SN1r4hzpjFKFLbZnBt77ACSiYx+IHK4Mp"
                "+NaVEi5wQtSsjQtI++XsokxRDqYLwus1I1SihgbV/STTg5en"
                "ufuwIDAQABo2IwYDBeBgNVHQEEVzBVgBDLebM6bK3BjWGqIBrBNFeNoS8wLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJ"
                "vbC53aW5kb3dzLm5ldIIQsRiM0jheFZhKk49YD0SK1TAJBgUrDgMCHQUAA4IBAQCJ4JApryF77EKC4zF5bUaBLQHQ1PNtA1uMDbdN"
                "VGKCmSf8M65b8h0NwlIjGGGy"
                "/unK8P6jWFdm5IlZ0YPTOgzcRZguXDPj7ajyvlVEQ2K2ICvTYiRQqrOhEhZMSSZsTKXFVwNfW6ADD"
                "kN3bvVOVbtpty+nBY5UqnI7xbcoHLZ4wYD251uj5"
                "+lo13YLnsVrmQ16NCBYq2nQFNPuNJw6t3XUbwBHXpF46aLT1/eGf/7Xx6iy8y"
                "PJX4DyrpFTutDz882RWofGEO5t4Cw+zZg70dJ/hH/ODYRMorfXEW"
                "+8uKmXMKmX2wyxMKvfiPbTy5LmAU8Jvjs2tLg4rOBcXWLAIarZ"
            ],
            "x5t": "kriMPdmBvx68skT8-mPAB3BseeA"
        },
        {
            "e": "AQAB",
            "issuer": "https://login.microsoftonline.com/{tenantid}/v2.0/",
            "kid": "MnC_VZcATfM5pOYiJHMba9goEKY",
            "kty": "RSA",
            "n":
                "vIqz-4-ER_vNWLON9yv8hIYV737JQ6rCl6XfzOC628seYUPf0TaGk91CFxefhzh23V9Tkq-RtwN1Vs_z57hO82kkzL-cQHZX3bMJ"
                 "D-GEGOKXCEXURN7VMyZWMAuzQoW9vFb1k3cR1RW_EW_P"
                "-C8bb2dCGXhBYqPfHyimvz2WarXhntPSbM5XyS5v5yCw5T_Vuwqqsio3"
                 "V8wooWGMpp61y12NhN8bNVDQAkDPNu2DT9DXB1g0CeFINp_KAS_qQ2Kq6TSvRHJqxRR68RezYtje9KAqwqx4jxlmVAQy0T3-T-IA"
                 "bsk1wRtWDndhO6s1Os-dck5TzyZ_dNOhfXgelixLUQ",
            "use": "sig",
            "x5c": [
                "MIIC4jCCAcqgAwIBAgIQQNXrmzhLN4VGlUXDYCRT3zANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb"
                "250cm9sLndpbmRvd3MubmV0MB4XDTE0MTAyODAwMDAwMFoXDTE2MTAyNzAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZX"
                "NzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALyKs/uPhEf7zVizjfcr/ISGFe9+yUO"
                "qwpel38zgutvLHmFD39E2hpPdQhcXn4c4dt1fU5KvkbcDdVbP8+e4TvNpJMy"
                "/nEB2V92zCQ/hhBjilwhF1ETe1TMmVjALs0KFvbxW"
                "9ZN3EdUVvxFvz/gvG29nQhl4QWKj3x8opr89lmq14Z7T0mzOV8kub+cgsOU"
                "/1bsKqrIqN1fMKKFhjKaetctdjYTfGzVQ0AJAzzbtg"
                "0/Q1wdYNAnhSDafygEv6kNiquk0r0RyasUUevEXs2LY3vSgKsKseI8ZZlQEMtE9/k/iAG7JNcEbVg53YTurNTrPnXJOU88mf3TToX"
                "14HpYsS1ECAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAfolx45w0i8CdAUjjeAaYdhG9+NDHxop0UvNOqlGqYJexqPLuvX8iyUaYxNG"
                "zZxFgGI3GpKfmQP2JQWQ1E5JtY/n8iNLOKRMwqkuxSCKJxZJq4Sl/m"
                "/Yv7TS1P5LNgAj8QLCypxsWrTAmq2HSpkeSk4JBtsYxX6uh"
                "bGM/K1sEktKybVTHu22/7TmRqWTmOUy9wQvMjJb2IXdMGLG3hVntN"
                "/WWcs5w8vbt1i8Kk6o19W2MjZ95JaECKjBDYRlhG1KmSBtrs"
                "KsCBQoBzwH/rXfksTO9JoUYLXiW0IppB7DhNH4PJ5hZI91R8rR0H3"
                "/bKkLSuDaKLWSqMhozdhXsIIKvJQ=="
            ],
            "x5t": "MnC_VZcATfM5pOYiJHMba9goEKY"
        },
        {
            "e": "AQAB",
            "issuer": "https://login.microsoftonline.com/9188040d-6c67-4c5b"
                      "-b112-36a304b66dad/v2.0/",
            "kid": "GvnPApfWMdLRi8PDmisFn7bprKg",
            "kty": "RSA",
            "n": "5ymq_xwmst1nstPr8YFOTyD1J5N4idYmrph7AyAv95RbWXfDRqy8CMRG7sJq"
                 "-UWOKVOA4MVrd_NdV-ejj1DE5MPSiG"
                 "-mZK_5iqRCDFvPYqOyRj539xaTlARNY4jeXZ0N6irZYKqSfYACjkkKxbLKcijSu1pJ48thXOTED0oNa6U",
            "use": "sig",
            "x5c": [
                "MIICWzCCAcSgAwIBAgIJAKVzMH2FfC12MA0GCSqGSIb3DQEBBQUAMCkxJzAlBgNVBAMTHkxpdmUgSUQgU1RTIFNpZ25pbmcgUHVib"
                "GljIEtleTAeFw0xMzExMTExODMzMDhaFw0xNjExMTAxODMzMDhaMCkxJzAlBgNVBAMTHkxpdmUgSUQgU1RTIFNpZ25pbmcgUHVibG"
                "ljIEtleTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEA5ymq"
                "/xwmst1nstPr8YFOTyD1J5N4idYmrph7AyAv95RbWXfDRqy8CMR"
                "G7sJq+UWOKVOA4MVrd/NdV+ejj1DE5MPSiG+mZK"
                "/5iqRCDFvPYqOyRj539xaTlARNY4jeXZ0N6irZYKqSfYACjkkKxbLKcijSu1pJ"
                "48thXOTED0oNa6UCAwEAAaOBijCBhzAdBgNVHQ4EFgQURCN"
                "+4cb0pvkykJCUmpjyfUfnRMowWQYDVR0jBFIwUIAURCN+4cb0pvkyk"
                "JCUmpjyfUfnRMqhLaQrMCkxJzAlBgNVBAMTHkxpdmUgSUQgU1RTIFNpZ25pbmcgUHVibGljIEtleYIJAKVzMH2FfC12MAsGA1UdDw"
                "QEAwIBxjANBgkqhkiG9w0BAQUFAAOBgQB8v8G5"
                "/vUl8k7xVuTmMTDA878AcBKBrJ/Hp6RShmdqEGVI7SFR7IlBN1//NwD0n"
                "+Iqzmn"
                "RV2PPZ7iRgMF/Fyvqi96Gd8X53ds/FaiQpZjUUtcO3fk0hDRQPtCYMII5jq"
                "+YAYjSybvF84saB7HGtucVRn2nMZc5cAC42QNYIlPM"
                "qA=="
            ],
            "x5t": "GvnPApfWMdLRi8PDmisFn7bprKg"
        },
        {
            "e": "AQAB",
            "issuer": "https://login.microsoftonline.com/9188040d-6c67-4c5b"
                      "-b112-36a304b66dad/v2.0/",
            "kid": "dEtpjbEvbhfgwUI-bdK5xAU_9UQ",
            "kty": "RSA",
            "n":
                "x7HNcD9ZxTFRaAgZ7-gdYLkgQua3zvQseqBJIt8Uq3MimInMZoE9QGQeSML7qZPlowb5BUakdLI70ayM4vN36--0ht8-oCHhl8Yj"
                 "GFQkU-Iv2yahWHEP-1EK6eOEYu6INQP9Lk0HMk3QViLwshwb"
                "-KXVD02jdmX2HNdYJdPyc0c",
            "use": "sig",
            "x5c": [
                "MIICWzCCAcSgAwIBAgIJAL3MzqqEFMYjMA0GCSqGSIb3DQEBBQUAMCkxJzAlBgNVBAMTHkxpdmUgSUQgU1RTIFNpZ25pbmcgUHVib"
                "GljIEtleTAeFw0xMzExMTExOTA1MDJaFw0xOTExMTAxOTA1MDJaMCkxJzAlBgNVBAMTHkxpdmUgSUQgU1RTIFNpZ25pbmcgUHVibG"
                "ljIEtleTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAx7HNcD9ZxTFRaAgZ7+gdYLkgQua3zvQseqBJIt8Uq3MimInMZoE9QGQ"
                "eSML7qZPlowb5BUakdLI70ayM4vN36++0ht8+oCHhl8YjGFQkU"
                "+Iv2yahWHEP+1EK6eOEYu6INQP9Lk0HMk3QViLwshwb+KXVD02j"
                "dmX2HNdYJdPyc0cCAwEAAaOBijCBhzAdBgNVHQ4EFgQULR0aj9AtiNMgqIY8ZyXZGsHcJ5gwWQYDVR0jBFIwUIAULR0aj9AtiNMgq"
                "IY8ZyXZGsHcJ5ihLaQrMCkxJzAlBgNVBAMTHkxpdmUgSUQgU1RTIFNpZ25pbmcgUHVibGljIEtleYIJAL3MzqqEFMYjMAsGA1UdDw"
                "QEAwIBxjANBgkqhkiG9w0BAQUFAAOBgQBshrsF9yls4ArxOKqXdQPDgHrbynZL8m1iinLI4TeSfmTCDevXVBJrQ6SgDkihl3aCj74"
                "IEte2MWN78sHvLLTWTAkiQSlGf1Zb0durw+OvlunQ2AKbK79Qv0Q+wwGuK"
                "+oymWc3GSdP1wZqk9dhrQxb3FtdU2tMke01QTut6wr7"
                "ig=="
            ],
            "x5t": "dEtpjbEvbhfgwUI-bdK5xAU_9UQ"
        }
    ]
}


# def test_key_setup():
#     x = key_setup()


def test_build_keyjar():
    keys = [
        {"type": "RSA", "use": ["enc", "sig"]},
        {"type": "EC", "crv": "P-256", "use": ["sig"]},
    ]

    jwks, keyjar, kidd = build_keyjar(keys)
    for key in jwks["keys"]:
        assert "d" not in key  # the JWKS shouldn't contain the private part
        # of the keys

    assert len(keyjar[""]) == 2  # 1 with RSA keys and 1 with EC key

    assert "RSA" in kidd["enc"]
    assert "RSA" in kidd["sig"]
    assert "EC" in kidd["sig"]


def test_build_keyjar_missing(tmpdir):
    keys = [
        {"type": "RSA", "key": os.path.join(tmpdir.dirname, "missisng_file"),
         "use": ["enc", "sig"]}]

    jwks, keyjar, kidd = build_keyjar(keys)

    assert len(keyjar[""]) == 1

    assert "RSA" in kidd["enc"]
    assert "RSA" in kidd["sig"]


def test_key_export():
    kj = KeyJar()
    url = key_export("http://example.com/keys/", "outbound", "secret",
                     keyjar=kj, sig={"alg": "rsa", "format": ["x509", "jwks"]})

    assert url == "http://example.com/keys/outbound/jwks"

    # Now a jwks should reside in './keys/outbound/jwks'

    kb = KeyBundle(source='file://./keys/outbound/jwks')

    # One key
    assert len(kb) == 1
    # more specifically one RSA key
    assert len(kb.get('RSA')) == 1
    k = kb.get('RSA')[0]
    # For signing
    assert k.use == 'sig'


class TestKeyJar(object):
    def test_keyjar_add(self):
        kj = KeyJar()
        kb = keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"])
        kj.add_kb('https://issuer.example.com', kb)
        assert list(kj.owners()) == ['https://issuer.example.com']

    def test_setitem(self):
        kj = KeyJar()
        kb = keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"])
        kj['https://issuer.example.com'] = kb
        assert list(kj.owners()) == ['https://issuer.example.com']

    def test_add_symmetric(self):
        kj = KeyJar()
        kj.add_symmetric('', 'client_secret', ['sig'])
        assert list(kj.owners()) == ['']
        assert len(kj.get_signing_key('oct', '')) == 1

    def test_items(self):
        ks = KeyJar()
        ks[""] = KeyBundle([{"kty": "oct", "key": "a1b2c3d4", "use": "sig"},
                            {"kty": "oct", "key": "a1b2c3d4", "use": "ver"}])
        ks["http://www.example.org"] = KeyBundle([
            {"kty": "oct", "key": "e5f6g7h8", "use": "sig"},
            {"kty": "oct", "key": "e5f6g7h8", "use": "ver"}])
        ks["http://www.example.org"].append(
            keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"]))

        assert len(ks.items()) == 2

    def test_issuer_extra_slash(self):
        ks = KeyJar()
        ks[""] = KeyBundle([{"kty": "oct", "key": "a1b2c3d4", "use": "sig"},
                            {"kty": "oct", "key": "a1b2c3d4", "use": "ver"}])
        ks["http://www.example.org"] = KeyBundle([
            {"kty": "oct", "key": "e5f6g7h8", "use": "sig"},
            {"kty": "oct", "key": "e5f6g7h8", "use": "ver"}])
        ks["http://www.example.org"].append(
            keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"]))

        assert ks.get('sig', 'RSA', 'http://www.example.org/')

    def test_issuer_missing_slash(self):
        ks = KeyJar()
        ks[""] = KeyBundle([{"kty": "oct", "key": "a1b2c3d4", "use": "sig"},
                            {"kty": "oct", "key": "a1b2c3d4", "use": "ver"}])
        ks["http://www.example.org/"] = KeyBundle([
            {"kty": "oct", "key": "e5f6g7h8", "use": "sig"},
            {"kty": "oct", "key": "e5f6g7h8", "use": "ver"}])
        ks["http://www.example.org/"].append(
            keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"]))

        assert ks.get('sig', 'RSA', 'http://www.example.org')

    def test_get_enc(self):
        ks = KeyJar()
        ks[""] = KeyBundle([{"kty": "oct", "key": "a1b2c3d4", "use": "sig"},
                            {"kty": "oct", "key": "a1b2c3d4", "use": "enc"}])
        ks["http://www.example.org/"] = KeyBundle([
            {"kty": "oct", "key": "e5f6g7h8", "use": "sig"},
            {"kty": "oct", "key": "e5f6g7h8", "use": "ver"}])
        ks["http://www.example.org/"].append(
            keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"]))

        assert ks.get('enc', 'oct')

    def test_get_enc_not_mine(self):
        ks = KeyJar()
        ks[""] = KeyBundle([{"kty": "oct", "key": "a1b2c3d4", "use": "sig"},
                            {"kty": "oct", "key": "a1b2c3d4", "use": "enc"}])
        ks["http://www.example.org/"] = KeyBundle([
            {"kty": "oct", "key": "e5f6g7h8", "use": "sig"},
            {"kty": "oct", "key": "e5f6g7h8", "use": "ver"}])
        ks["http://www.example.org/"].append(
            keybundle_from_local_file(RSAKEY, "der", ["ver", "sig"]))

        assert ks.get('enc', 'oct', 'http://www.example.org/')

    # def test_get_by_kid(self):
    #     kb = keybundle_from_local_file("file://%s/jwk.json" % BASE_PATH, "jwks",
    #                                    ["sig"])
    #     kj = KeyJar()
    #     kj.issuer_keys["https://example.com"] = [kb]
    #
    #     _key = kj.get_key_by_kid("abc", "https://example.com")
    #     assert _key
    #     assert _key.kid == "abc"

    def test_dump_issuer_keys(self):
        kb = keybundle_from_local_file("file://%s/jwk.json" % BASE_PATH, "jwks",
                                       ["sig"])
        assert len(kb) == 1
        kj = KeyJar()
        kj.issuer_keys[""] = [kb]
        _jwks_dict = kj.export_jwks()

        _info = _jwks_dict['keys'][0]
        assert _info == {
            'use': 'sig',
            'e': 'AQAB',
            'kty': 'RSA',
            'alg': 'RS256',
            'n': 'pKybs0WaHU_y4cHxWbm8Wzj66HtcyFn7Fh3n'
                 '-99qTXu5yNa30MRYIYfSDwe9JVc1JUoGw41yq2StdGBJ40HxichjE'
                 '-Yopfu3B58Q'
                 'lgJvToUbWD4gmTDGgMGxQxtv1En2yedaynQ73sDpIK-12JJDY55pvf'
                 '-PCiSQ9OjxZLiVGKlClDus44_uv2370b9IN2JiEOF-a7JB'
                 'qaTEYLPpXaoKWDSnJNonr79tL0T7iuJmO1l705oO3Y0TQ'
                 '-INLY6jnKG_RpsvyvGNnwP9pMvcP1phKsWZ10ofuuhJGRp8IxQL9Rfz'
                 'T87OvF0RBSO1U73h09YP-corWDsnKIi6TbzRpN5YDw',
            'kid': 'abc'}

    def test_no_use(self):
        kb = KeyBundle(JWK0["keys"])
        kj = KeyJar()
        kj.issuer_keys["abcdefgh"] = [kb]
        enc_key = kj.get_encrypt_key("RSA", "abcdefgh")
        assert enc_key != []

    @pytest.mark.network
    def test_provider(self):
        provider_info = {
            "jwks_uri": "https://connect-op.herokuapp.com/jwks.json",
        }

        ks = KeyJar()
        ks.load_keys(provider_info, "https://connect-op.heroku.com")

        assert ks["https://connect-op.heroku.com"][0].keys()


def test_import_jwks():
    kj = KeyJar()
    kj.import_jwks(JWK1, '')
    assert len(kj.get_issuer_keys('')) == 4


def test_get_signing_key_use_undefined():
    kj = KeyJar()
    kj.import_jwks(JWK1, '')
    keys = kj.get_signing_key(kid='rsa1')
    assert len(keys) == 1

    keys = kj.get_signing_key(key_type='rsa')
    assert len(keys) == 1

    keys = kj.get_signing_key(key_type='rsa', kid='rsa1')
    assert len(keys) == 1


KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]


def test_remove_after():
    # initial keyjar
    keyjar = build_keyjar(KEYDEFS)[1]
    _old = [k.kid for k in keyjar.get_issuer_keys('') if k.kid]
    assert len(_old) == 2

    # rotate_keys = create new keys + make the old as inactive
    keyjar = build_keyjar(KEYDEFS, keyjar=keyjar)[1]

    keyjar.remove_after = 1
    # None are remove since none are marked as inactive yet
    keyjar.remove_outdated()

    _interm = [k.kid for k in keyjar.get_issuer_keys('') if k.kid]
    assert len(_interm) == 4

    # Now mark the keys to be inactivated
    _now = time.time()
    for k in keyjar.get_issuer_keys(''):
        if k.kid in _old:
            if not k.inactive_since:
                k.inactive_since = _now

    keyjar.remove_outdated(_now + 5)

    # The remainder are the new keys
    _new = [k.kid for k in keyjar.get_issuer_keys('') if k.kid]
    assert len(_new) == 2

    # should not be any overlap between old and new
    assert set(_new).intersection(set(_old)) == set()


JWK_UK = {"keys": [
    {
        "n":
            "zkpUgEgXICI54blf6iWiD2RbMDCOO1jV0VSff1MFFnujM4othfMsad7H1kRo50YM5S_X9TdvrpdOfpz5aBaKFhT6Ziv0nhtcekq1eRl8"
             "mjBlvGKCE5XGk-0LFSDwvqgkJoFYInq7bu0a4JEzKs5AyJY75YlGh879k1Uu2Sv3ZZOunfV1O1Orta-NvS-aG_jN5cstVbCGWE20H0vF"
             "VrJKNx0Zf-u-aA-syM4uX7wdWgQ"
            "-owoEMHge0GmGgzso2lwOYf_4znanLwEuO3p5aabEaFoKNR4K6GjQcjBcYmDEE4CtfRU9AEmhcD1k"
             "leiTB9TjPWkgDmT9MXsGxBHf3AKT5w",
        "e": "AQAB", "kty": "RSA", "kid": "rsa1"},
    {
        "k":
            "YTEyZjBlMDgxMGI4YWU4Y2JjZDFiYTFlZTBjYzljNDU3YWM0ZWNiNzhmNmFlYTNkNTY0NzMzYjE",
        "kty": "buz"},
]}


def test_load_unknown_keytype():
    kj = KeyJar()
    kj.import_jwks(JWK_UK, '')
    assert len(kj.get_issuer_keys('')) == 2


JWK_FP = {"keys": [
    {"e": "AQAB", "kty": "RSA", "kid": "rsa1"},
]}


def test_load_missing_key_parameter():
    kj = KeyJar()
    kj.import_jwks(JWK_FP, '')
    assert len(kj.get_issuer_keys('')) == 0


JWKS_SPO = {
    "keys": [
        {
            "kid":
                "BfxfnahEtkRBG3Hojc9XGLGht_5rDBj49Wh3sBDVnzRpulMqYwMRmpizA0aSPT1fhCHYivTiaucWUqFu_GwTqA",
            "use": "sig",
            "alg": "ES256",
            "kty": "EC",
            "crv": "P-256",
            "x": "1XXUXq75gOPZ4bEj1o2Z5XKJWSs6LmL6fAOK3vyMzSc",
            "y": "ac1h_DwyuUxhkrD9oKMJ-b_KuiVvvSARIwT-XoEmDXs"
        },
        {
            "kid":
                "91pD1H81rXUvrfg9mkngIG-tXjnldykKUVbITDIU1SgJvq91b8clOcJuEHNAq61eIvg8owpEvWcWAtlbV2awyA",
            "use": "sig",
            "alg": "ES256",
            "kty": "EC",
            "crv": "P-256",
            "x": "2DfQoLpZS2j3hHEcHDkzV8ISx-RdLt6Opy8YZYVm4AQ",
            "y": "ycvkFMBIzgsowiaf6500YlG4vaMSK4OF7WVtQpUbEE0"
        },
        {
            "kid": "0sIEl3MUJiCxrqleEBBF-_bZq5uClE84xp-wpt8oOI"
                   "-WIeNxBjSR4ak_OTOmLdndB0EfDLtC7X1JrnfZILJkxA",
            "use": "sig",
            "alg": "RS256",
            "kty": "RSA",
            "n":
                "yG9914Q1j63Os4jX5dBQbUfImGq4zsXJD4R59XNjGJlEt5ek6NoiDl0ucJO3_7_R9e5my2ONTSqZhtzFW6MImnIn8idWYzJzO2EhUPCHTvw_2oOGjeYTE2VltIyY_ogIxGwY66G0fVPRRH9tCxnkGOrIvmVgkhCCGkamqeXuWvx9MCHL_gJbZJVwogPSRN_SjA1gDlvsyCdA6__CkgAFcSt1sGgiZ_4cQheKexxf1-7l8R91ZYetz53drk2FS3SfuMZuwMM4KbXt6CifNhzh1Ye-5Tr_ZENXdAvuBRDzfy168xnk9m0JBtvul9GoVIqvCVECB4MPUb7zU6FTIcwRAw",
            "e": "AQAB"
        },
        {
            "kid":
                "zyDfdEU7pvH0xEROK156ik8G7vLO1MIL9TKyL631kSPtr9tnvs9XOIiq5jafK2hrGr2qqvJdejmoonlGqWWZRA",
            "use": "sig",
            "alg": "RS256",
            "kty": "RSA",
            "n":
                "68be-nJp46VLj4Ci1V36IrVGYqkuBfYNyjQTZD_7yRYcERZebowOnwr3w0DoIQpl8iL2X8OXUo7rUW_LMzLxKx2hEmdJfUn4LL2QqA3KPgjYz8hZJQPG92O14w9IZ-8bdDUgXrg9216H09yq6ZvJrn5Nwvap3MXgECEzsZ6zQLRKdb_R96KFFgCiI3bEiZKvZJRA7hM2ePyTm15D9En_Wzzfn_JLMYgE_DlVpoKR1MsTinfACOlwwdO9U5Dm-5elapovILTyVTgjN75i-wsPU2TqzdHFKA-4hJNiWGrYPiihlAFbA2eUSXuEYFkX43ahoQNpeaf0mc17Jt5kp7pM2w",
            "e": "AQAB"
        },
        {
            "kid": "q-H9y8iuh3BIKZBbK6S0mH_isBlJsk"
                   "-u6VtZ5rAdBo5fCjjy3LnkrsoK_QWrlKB08j_PcvwpAMfTEDHw5spepw",
            "use": "sig",
            "alg": "EdDSA",
            "kty": "OKP",
            "crv": "Ed25519",
            "x": "FnbcUAXZ4ySvrmdXK1MrDuiqlqTXvGdAaE4RWZjmFIQ"
        },
        {
            "kid":
                "bL33HthM3fWaYkY2_pDzUd7a65FV2R2LHAKCOsye8eNmAPDgRgpHWPYpWFVmeaujUUEXRyDLHN-Up4QH_sFcmw",
            "use": "sig",
            "alg": "EdDSA",
            "kty": "OKP",
            "crv": "Ed25519",
            "x": "CS01DGXDBPV9cFmd8tgFu3E7eHn1UcP7N1UCgd_JgZo"
        }
    ]
}


def test_load_spomky_keys():
    kj = KeyJar()
    kj.import_jwks(JWKS_SPO, '')
    assert len(kj.get_issuer_keys('')) == 4


def test_get_ec():
    kj = KeyJar()
    kj.import_jwks(JWKS_SPO, '')
    k = kj.get('sig', 'EC', alg='ES256')
    assert k


def test_get_ec_wrong_alg():
    kj = KeyJar()
    kj.import_jwks(JWKS_SPO, '')
    k = kj.get('sig', 'EC', alg='ES512')
    assert k == []


def test_keyjar_eq():
    kj1 = KeyJar()
    kj1.import_jwks(JWKS_SPO, '')

    kj2 = KeyJar()
    kj2.import_jwks(JWKS_SPO, '')

    assert kj1 == kj2


def test_keys_by_alg_and_usage():
    kj = KeyJar()
    kj.import_jwks(JWKS_SPO, '')
    k = kj.keys_by_alg_and_usage('', 'RS256', 'sig')
    assert len(k) == 2


class TestVerifyJWTKeys(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        mkey = [
            {"type": "RSA", "use": ["sig"]},
            {"type": "RSA", "use": ["sig"]},
            {"type": "RSA", "use": ["sig"]},
        ]

        skey = [
            {"type": "RSA", "use": ["sig"]},
        ]

        kj1 = build_keyjar(mkey)[1]
        kj2 = build_keyjar(skey)[1]
        self.keyjar = KeyJar()
        self.keyjar['A'] = kj1['']
        self.keyjar['B'] = kj2['']

        _jws = JWS('{"aud": "A"}', alg='RS256')
        sig_key = self.keyjar.get_signing_key('rsa',owner='A')[0]
        self.sjwt_a = _jws.sign_compact([sig_key])

        _jws = JWS('{"aud": "B"}', alg='RS256')
        sig_key = self.keyjar.get_signing_key('rsa',owner='B')[0]
        self.sjwt_b = _jws.sign_compact([sig_key])

    def test_no_kid_multiple_keys(self):
        """ This is extremely strict """
        _jwt = factory(self.sjwt_a)
        # remove kid reference
        _jwt.jwt.headers['kid'] = ''
        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt)
        assert len(keys) == 0

    def test_no_kid_single_key(self):
        _jwt = factory(self.sjwt_b)
        _jwt.jwt.headers['kid'] = ''
        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt)
        assert len(keys) == 1

    def test_no_kid_multiple_keys_no_kid_issuer(self):
        a_kids = [k.kid for k in
                  self.keyjar.get_verify_key(owner='A', key_type='RSA')]
        no_kid_issuer = {'A': a_kids}
        _jwt = factory(self.sjwt_a)
        _jwt.jwt.headers['kid'] = ''
        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt,
                                               no_kid_issuer=no_kid_issuer)
        assert len(keys) == 3
        assert set([k.kid for k in keys]) == set(a_kids)

    def test_no_kid_multiple_keys_no_kid_issuer_lim(self):
        a_kids = [k.kid for k in
                  self.keyjar.get_verify_key(owner='A', key_type='RSA')]
        no_kid_issuer = {'A': []}
        _jwt = factory(self.sjwt_a)
        _jwt.jwt.headers['kid'] = ''
        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt,
                                               no_kid_issuer=no_kid_issuer)
        assert len(keys) == 3
        assert set([k.kid for k in keys]) == set(a_kids)

    def test_matching_kid(self):
        _jwt = factory(self.sjwt_b)
        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt)
        assert len(keys) == 1

    def test_no_matching_kid(self):
        _jwt = factory(self.sjwt_b)
        _jwt.jwt.headers['kid'] = 'abcdef'
        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt)
        assert keys == []

    def test_aud(self):
        self.keyjar.import_jwks(JWK1, issuer='D')

        _jws = JWS('{"iss": "D", "aud": "A"}', alg='HS256')
        sig_key = self.keyjar.get_signing_key('oct', owner='D')[0]
        _sjwt = _jws.sign_compact([sig_key])

        no_kid_issuer = {'D': []}

        _jwt = factory(_sjwt)

        keys = self.keyjar.get_jwt_verify_keys(_jwt.jwt,
                                               no_kid_issuer=no_kid_issuer)
        assert len(keys) == 1


def test_copy():
    kj = KeyJar()
    kj['A'] = [KeyBundle(JWK0['keys'])]
    kj['B'] = [KeyBundle(JWK1['keys'])]
    kj['C'] = [KeyBundle(JWK2['keys'])]

    kjc = kj.copy()

    assert set(kjc.owners()) == {'A', 'B', 'C'}

    assert len(kjc.get('sig', 'oct', 'A')) == 0
    assert len(kjc.get('sig', 'rsa', 'A')) == 1

    assert len(kjc.get('sig', 'oct', 'B')) == 1
    assert len(kjc.get('sig', 'rsa', 'B')) == 1

    assert len(kjc.get('sig', 'oct', 'C')) == 0
    assert len(kjc.get('sig', 'rsa', 'C')) == 4