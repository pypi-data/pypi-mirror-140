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

from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    """
    A transaction in a block in the ethereum blockchain.
    """
    parent_block_number: str
    parent_block_hash: str
    from_: str
    to: str
    hash: str
    input_: str


@dataclass
class Block:
    """
    A block in the blockchain.
    """
    block_hash: str
    parent_block_hash_id: str
    transaction_hashes: list[str]


@dataclass
class NFT:
    """A Non-Fungiable Token "on" the blockchain

    Repreresents an NFT that is recorded on the blockchain.

    :arg token_url: URL Of the NFT resource.
    :type token_url: str
    :arg token_id: ID of the NFT in its  contract.
    :type token_id: int
    :arg issuing_contract_address: Address of the ERC-721
        smart contract that issued the NFT token.
    :type issuing_contract_address: str
    :arg minting_transaction_hash: Hash of the transaction
        that minted the token.
    :type minting_transaction_hash: str
    """
    token_url: str
    token_id: int
    issuing_contract_address: str
    minting_transaction_hash: str
