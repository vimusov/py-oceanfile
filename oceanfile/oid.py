"""
    This file is part of oceanfile.

    oceanfile is free software: you can redistribute it and/or modify it under the terms
    of the GNU General Public License as published by the Free Software Foundation, either
    version 3 of the License, or (at your option) any later version.

    oceanfile is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty     of MERCHANTABILITY or FITNESS FOR A PARTICULAR
    PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with oceanfile.
    If not, see <https://www.gnu.org/licenses/>.
"""

from uuid import uuid4


def create_oid() -> str:
    """
    As I found it's better when OID is random. Because when it's static it takes too much time
    to update directories list on the mobile device. As an alternative it's a good idea to create
    OID from a directory name using hashing function like MD5.
    """
    return str(uuid4())
