# OpENWatch
# Copyright (C) 2021  Ege Emir Özkan

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class InvalidMintTransactionException(Exception):
    """
    Given transaction is not a mint transaction but was
        handled as one.
    """

    def __init__(self, transaction_hash: str, *args: object) -> None:
        super().__init__(
            f'Transaction with the hash {transaction_hash} is not a mint transaction', *args)


class TransactionCouldNotFetch(Exception):
    """
    Given transaction couldn't be fetched
    """

    def __init__(self, transaction_hash: str, *args: object) -> None:
        super().__init__(
            f'Transaction with the hash {transaction_hash} couldn\'t be fetched', *args)


class CouldNotFetchNFTURL(Exception):
    """
    Given NFT URL couldn't be fetched
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
