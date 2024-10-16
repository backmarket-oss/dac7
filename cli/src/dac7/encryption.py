from __future__ import annotations

from hashlib import sha512
from io import BytesIO
from zipfile import ZipFile

from dac7.constants import Env

import requests

from gnupg import GPG


class KeyInfo:
    fingerprint: str
    archive_url: str
    archive_checksum: str

    @classmethod
    def for_env(cls, env: Env) -> KeyInfo:
        return KeyInfoProd() if env == Env.PROD else KeyInfoTest()


class KeyInfoProd(KeyInfo):
    fingerprint = "3AE282C69675932A19D3245BD155B53F9EFF7A61"
    archive_url = "https://www.impots.gouv.fr/sites/default/files/media/1_metier/3_partenaire/tiers_declarants/cdc_td_bilateral/cle_publique_chiffrement_dgfip_tiersdeclarants_prod.zip"
    archive_checksum = (
        "c3350b1db0a7e9536892254fcd796e702f9dad0be12f97032c32349405bc5b0a1ca868"
        "6997240f686e3e302678791644577924ccb72b236ad1df2431a78b66a8"
    )


class KeyInfoTest(KeyInfo):
    fingerprint = "E7125CD404D160E6C1C773299182BFA4B2FCE419"
    archive_url = "https://www.impots.gouv.fr/sites/default/files/media/1_metier/3_partenaire/tiers_declarants/cdc_td_bilateral/cle_publique_chiffrement_dgfip_tiersdeclarants_test.zip"
    archive_checksum = (
        "ec7f4ec691f6b8a846969b95d8c04b4bf699099adca0d56367248bccd64cd8c57f4315"
        "27e10335cc454424b7952cb80a222e4b27a0f89cfdff014425ffdcfd42"
    )


class EncryptionService:

    def __init__(self, key_info: KeyInfo):
        self.gpg = GPG()
        self.key_info = key_info

    def encrypt_data(self, data: bytes) -> bytes:
        self.import_key_to_gpg()
        result = self.gpg.encrypt(
            data,
            recipients=self.key_info.fingerprint,
            always_trust=True,
            armor=False,
        )
        if not result.ok:
            raise Exception(result.stderr)

        return result.data

    def import_key_to_gpg(self) -> None:
        for key_info in self.gpg.list_keys():
            if self.key_info.fingerprint in key_info["fingerprint"]:
                return

        key = self.fetch_key()
        result = self.gpg.import_keys(key, extra_args=["--yes"])
        if not result.count:
            raise Exception(result.stderr)

    def fetch_key(self) -> str:
        key_archive = self.get_key_archive()
        for file_name in key_archive.namelist():
            if file_name.endswith(".asc"):
                return key_archive.read(file_name).decode("utf8")
        raise FileNotFoundError()

    def get_key_archive(self) -> ZipFile:
        response = requests.get(self.key_info.archive_url, timeout=30)
        response.raise_for_status()

        content = response.content
        if sha512(content).hexdigest() != self.key_info.archive_checksum:
            raise ValueError()

        stream = BytesIO(content)
        return ZipFile(stream)
