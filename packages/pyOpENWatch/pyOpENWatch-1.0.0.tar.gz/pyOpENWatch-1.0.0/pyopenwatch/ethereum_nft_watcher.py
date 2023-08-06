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

from functools import lru_cache
from typing import Any, Callable, Optional
from uuid import uuid4
import logging

from requests import post

from .ethereum_classes import Block, Transaction, NFT
from .ethereum_utility import decode_return_value, decode_uint256_integer
from .ethereum_exceptions import InvalidMintTransactionException, TransactionCouldNotFetch, CouldNotFetchNFTURL


class EthereumNFTWatcher:
    def __init__(self, host: str, port: str, log_level: int) -> None:
        """
        Initialise an NFT tracker.

        :param host: Host address of the server.
        :param port: Port of the server.
        """
        self.address = f'{host}:{port}'
        logging.basicConfig()
        self.logger = logging.getLogger('OpENWatchLogger')
        self.logger.setLevel(log_level)

    def _send_json_rpc(self, method_name: str, params: list[Any]) -> Any:
        """
        Send a JSON RPC request to the Geth Server.

        :param method_name: Name of the method to be executed by RPC
            server.
        :param params: Parameters of the request
        :return The result key of the server response.
        """
        response = post(self.address, json={
            'jsonrpc': '2.0',
            'id': uuid4().int,
            'method': method_name,
            'params': params
        })
        return response.json()['result']

    @property
    def _latest_block(self) -> Block:
        """
        Return the latest block from the blockchain.

        :return the latest block from the blockchain.
        """
        block_data = self._send_json_rpc(
            'eth_getBlockByNumber', ['latest', False])
        return Block(block_data['hash'],
                     block_data['parentHash'],
                     block_data['transactions'])

    def _fetch_block(self, hash: str) -> Block:
        """
        Return the block with given hash.

        :param hash: Hash of the block.
        :return the Block with the given hash.
        """
        block_data = self._send_json_rpc(
            'eth_getBlockByHash', [hash, False])
        return Block(block_data['hash'],
                     block_data['parentHash'],
                     block_data['transactions'])

    def _fetch_transaction(self, transaction_hash: str) -> Transaction:
        """
        Return a transaction given its ID.

        :param transaction_id: The ID of the transaction
            to be fetched.

        :return the Transaction.
        """
        transaction_data = self._send_json_rpc(
            'eth_getTransactionByHash', [transaction_hash]
        )
        try:
            return Transaction(
                transaction_data['blockNumber'],
                transaction_data['blockHash'],
                transaction_data['from'],
                transaction_data['to'],
                transaction_data['hash'],
                transaction_data['input']
            )
        except TypeError:
            raise TransactionCouldNotFetch(transaction_hash)

    def _fetch_nft_id_from_transaction(self, transaction_hash: str) -> int:
        """
        Return the ID of an NFT minted in the given transaction hash.
        """
        receipt = self._send_json_rpc(
            'eth_getTransactionReceipt', [transaction_hash]
        )
        try:
            return decode_uint256_integer(receipt['logs'][0]['topics'][3])
        except (KeyError, TypeError, IndexError):
            self.logger.debug(
                f'Transaction {transaction_hash} is a non-mint transaction on a NFT.')
            raise InvalidMintTransactionException(transaction_hash)

    def _fetch_nft_url(self, smart_contract_address: str, nft_id: int) -> str:
        """
        Get the URL of the NFT token, this value is known as TokenURI internally    
            and can be fetched by calling the tokenURI(uint256 tokenID) function.

        :param smart_contract_address: Address of the smart contract on the EVM.
        :param nft_id: ID of the NFT token.
        """
        # We are calling the tokenURI(uint256 tokenID) function of the smart
        # contract in the locationNFT
        try:
            token_uri_raw = self._send_json_rpc(
                'eth_call',
                [
                    {
                        'to': smart_contract_address,
                        'data': f'0xc87b56dd{nft_id.to_bytes(256, "big").hex()}'
                    },
                    'latest'
                ]
            )
            return decode_return_value(token_uri_raw)
        except KeyError:
            self.logger.error(
                'Could not fetch URL of NFT with ID %s in %s',
                nft_id,
                smart_contract_address)
            raise CouldNotFetchNFTURL

    def _fetch_code_at_memory_address(self, contract_address: str) -> str:
        """
        Return the source code stored in the memory address in the EVM,
            in smart contracts there is code, in wallet addresses, there
            isn't.
        """
        code = self._send_json_rpc(
            'eth_getCode',
            [contract_address, 'latest']
        )
        return code

    @lru_cache(maxsize=2056)
    def _is_nft(self, contract_address: str) -> bool:
        """
        Check if the given adress is an NFT smart contract.
        """
        # We can do this by checking if the address contains code
        # With the hash 0xc87b56dd, which is the Keccak-256 hash
        # of the tokenURI method, because that's how Ethereum blockchain
        # decided to work, apperantly.
        if 'c87b56dd' in self._fetch_code_at_memory_address(contract_address):
            self.logger.info(
                f'Found {contract_address} to be a ERC-721 Compliant Smart Contract')
            return True
        return False

    def fetch_nfts_until_block(self, terminal_block_hash: str = f'0x{"0" * 64}', limit: int = -1, callback: Optional[Callable[[NFT], None]] = None) -> list[NFT]:
        """
        Return a list of NFTs minted in transaction that have occurred between the
            latest block in the Ethereum blockchain and the block with the given
            block hash (or before the given limit of blocks are exceeded).

        :param terminal_block_hash: The hash of the latest block to be fetched,
            if not provided, go to the first block.
        :param limit: Maximum number of blocks to be fetched, if not provided,
            ignored.
        :param callback: Function to be called with the latest fetched
            NFT whenever an NFT is fetched, if not provided, nothing is done.
        :return the list of NFTs.
        """
        nfts = []
        block_count = 0
        last_block_hash = self._latest_block.block_hash
        prev_block_hash = last_block_hash
        while prev_block_hash != terminal_block_hash and (block_count <= limit or limit == -1):
            self.logger.debug('Fetching block with hash %s', prev_block_hash)
            last_block = self._fetch_block(prev_block_hash)
            for transaction_hash in last_block.transaction_hashes:
                self.logger.debug(
                    f'Fetching transaction {transaction_hash}')
                try:
                    transaction = self._fetch_transaction(transaction_hash)
                except TransactionCouldNotFetch:
                    self.logger.error(
                        'Could not fetch transaction %s.', transaction_hash)
                    continue
                address = transaction.to
                if address is None:
                    # Sometimes addresses are just null.
                    # For some reason ¯\_(ツ)_/¯.
                    self.logger.warning(
                        f'Null address transaction at hash {transaction.hash}.')
                    continue
                if self._is_nft(address):
                    try:
                        token_id = self._fetch_nft_id_from_transaction(
                            transaction_hash)
                        token_url = self._fetch_nft_url(address, token_id)
                        nft = NFT(token_url, token_id,
                                  address, transaction_hash)
                        nfts.append(nft)
                        self.logger.info(
                            'Transaction %s is a mint transaction for ERC-721 Contract %s',
                            transaction_hash,
                            address)
                        if callback is not None:
                            callback(nft)
                    except (InvalidMintTransactionException, CouldNotFetchNFTURL):
                        # Easier than actuall checking.
                        continue
            block_count += 1
            prev_block_hash = last_block.parent_block_hash_id
        return nfts
