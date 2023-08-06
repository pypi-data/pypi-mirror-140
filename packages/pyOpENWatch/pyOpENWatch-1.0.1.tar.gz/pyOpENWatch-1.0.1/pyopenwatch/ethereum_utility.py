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

def decode_return_value(value: str) -> str:
    """
    Decode an ethereum return value, which is typically a group of bytes
        posing as an uint256 beacuse why not, I suppose/
    """
    return int(value, base=16).to_bytes(256, 'big').replace(b'\x00', b'').decode('ascii').strip()


def decode_uint256_integer(value: str) -> int:
    return int(value, base=16)
