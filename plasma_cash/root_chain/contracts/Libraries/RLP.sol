pragma solidity ^0.4.18;

/**
* @title RLPReader
*
* RLPReader is used to read and parse RLP encoded data in memory.
*
* @author Andreas Olofsson (androlo1980@gmail.com)
*/

library RLP {
    uint constant DATA_SHORT_START = 0x80;
    uint constant DATA_LONG_START = 0xB8;
    uint constant LIST_SHORT_START = 0xC0;
    uint constant LIST_LONG_START = 0xF8;

    uint constant DATA_LONG_OFFSET = 0xB7;
    uint constant LIST_LONG_OFFSET = 0xF7;


    struct RLPItem {
        uint _unsafe_memPtr;    // Pointer to the RLP-encoded bytes.
        uint _unsafe_length;    // Number of bytes. This is the full length of the string.
    }

    struct Iterator {
        RLPItem _unsafe_item;   // Item that's being iterated over.
        uint _unsafe_nextPtr;   // Position of the next item in the list.
    }

    /* Encoder */

    function encodeList(bytes[] memory self) internal constant returns (bytes) {
        bytes memory list = _flatten(self);
        bytes memory encoded = _encode(list);
        return encoded;
    }

    /* Iterator */

    function next(Iterator memory self)
        internal
        constant
        returns (RLPItem memory subItem)
    {
        uint ptr = self._unsafe_nextPtr;
        uint itemLength = _itemLength(ptr);
        subItem._unsafe_memPtr = ptr;
        subItem._unsafe_length = itemLength;
        self._unsafe_nextPtr = ptr + itemLength;
    }

    function hasNext(Iterator memory self) internal constant returns (bool) {
        RLPItem memory item = self._unsafe_item;
        return self._unsafe_nextPtr < item._unsafe_memPtr + item._unsafe_length;
    }

    /* RLPItem */

    /// @dev Creates an RLPItem from an array of RLP encoded bytes.
    /// @param self The RLP encoded bytes.
    /// @return An RLPItem
    function toRLPItem(bytes memory self)
        internal
        constant
        returns (RLPItem memory)
    {
        uint len = self.length;
        uint memPtr;
        assembly {
            memPtr := add(self, 0x20)
        }
        return RLPItem(memPtr, len);
    }

    /// @dev Create an iterator.
    /// @param self The RLP item.
    /// @return An 'Iterator' over the item.
    function iterator(RLPItem memory self)
        internal
        constant
        returns (Iterator memory it)
    {
        uint ptr = self._unsafe_memPtr + _payloadOffset(self);
        it._unsafe_item = self;
        it._unsafe_nextPtr = ptr;
    }

    /// @dev Get the list of sub-items from an RLP encoded list.
    /// Warning: This requires passing in the number of items.
    /// @param self The RLP item.
    /// @return Array of RLPItems.
    function toList(RLPItem memory self, uint256 numItems)
        internal
        constant
        returns (RLPItem[] memory list)
    {
        list = new RLPItem[](numItems);
        Iterator memory it = iterator(self);
        uint idx;
        while (idx < numItems) {
            list[idx] = next(it);
            idx++;
        }
    }

    /// @dev Decode an RLPItem into a uint. This will not work if the
    /// RLPItem is a list.
    /// @param self The RLPItem.
    /// @return The decoded string.
    function toUint(RLPItem memory self) internal constant returns (uint data) {
        uint rStartPos;
        uint len;
        (rStartPos, len) = _decode(self);
        assembly {
            data := div(mload(rStartPos), exp(256, sub(32, len)))
        }
    }

    /// @dev Decode an RLPItem into an address. This will not work if the
    /// RLPItem is a list.
    /// @param self The RLPItem.
    /// @return The decoded string.
    function toAddress(RLPItem memory self)
        internal
        view
        returns (address data)
    {
        uint len;
        (, len) = _decode(self);
        require(len <= 20);
        return address(toUint(self));
    }

    /// @dev Return the RLP encoded bytes.
    /// @param self The RLPItem.
    /// @return The bytes.
    function toBytes(RLPItem memory self)
        internal
        constant
        returns (bytes memory bts)
    {
        uint len = self._unsafe_length;
        if (len == 0)
            return;
        bts = new bytes(len);
        uint btsPtr;
        assembly {
            btsPtr := add(bts, 0x20)
        }
        _memcpy(btsPtr, self._unsafe_memPtr, len);
    }

    /// @dev Decode an RLPItem into bytes. This will not work if the
    /// RLPItem is a list.
    /// @param self The RLPItem.
    /// @return The decoded string.
    function toData(RLPItem memory self)
        internal
        constant
        returns (bytes memory bts)
    {
        uint rStartPos;
        uint len;
        (rStartPos, len) = _decode(self);
        bts = new bytes(len);
        uint btsPtr;
        assembly {
            btsPtr := add(bts, 0x20)
        }
        _memcpy(btsPtr, rStartPos, len);
    }

    /* Internal functions */

    // Get the payload offset.
    function _payloadOffset(RLPItem memory self) private view returns (uint) {
        if (self._unsafe_length == 0)
            return 0;
        uint b0;
        uint memPtr = self._unsafe_memPtr;
        assembly {
            b0 := byte(0, mload(memPtr))
        }
        if (b0 < DATA_SHORT_START)
            return 0;
        if (b0 < DATA_LONG_START ||
            (b0 >= LIST_SHORT_START && b0 < LIST_LONG_START))
            return 1;
        if (b0 < LIST_SHORT_START)
            return b0 - DATA_LONG_OFFSET + 1;
        return b0 - LIST_LONG_OFFSET + 1;
    }

    // Get the full length of an RLP item.
    function _itemLength(uint memPtr) private view returns (uint len) {
        uint b0;
        assembly {
            b0 := byte(0, mload(memPtr))
        }
        if (b0 < DATA_SHORT_START) {
            len = 1;
        } else if (b0 < DATA_LONG_START) {
            len = b0 - DATA_SHORT_START + 1;
        } else if (b0 < LIST_SHORT_START) {
            assembly {
                let bLen := sub(b0, 0xB7) // bytes length (DATA_LONG_OFFSET)
                let dLen := div(mload(add(memPtr, 1)), exp(256, sub(32, bLen))) // data length
                len := add(1, add(bLen, dLen)) // total length
            }
        } else if (b0 < LIST_LONG_START) {
            len = b0 - LIST_SHORT_START + 1;
        } else {
            assembly {
                let bLen := sub(b0, 0xF7) // bytes length (LIST_LONG_OFFSET)
                let dLen := div(mload(add(memPtr, 1)), exp(256, sub(32, bLen))) // data length
                len := add(1, add(bLen, dLen)) // total length
            }
        }
    }

    // Get start position and length of the data.
    function _decode(RLPItem memory self)
        private
        view
        returns (uint memPtr, uint len)
    {
        uint b0;
        uint start = self._unsafe_memPtr;
        assembly {
            b0 := byte(0, mload(start))
        }
        if (b0 < DATA_SHORT_START) {
            memPtr = start;
            len = 1;
            return;
        }
        if (b0 < DATA_LONG_START) {
            len = self._unsafe_length - 1;
            memPtr = start + 1;
        } else {
            uint bLen;
            assembly {
                bLen := sub(b0, 0xB7) // DATA_LONG_OFFSET
            }
            len = self._unsafe_length - 1 - bLen;
            memPtr = start + bLen + 1;
        }
        return;
    }

    function _encode(bytes memory self)
        private
        constant
        returns (bytes memory bts)
    {
        uint selfPtr;
        assembly {
            selfPtr := add(self, 0x20)
        }

        bytes memory encoded;
        uint encodedPtr;

        uint len = self.length;
        uint lenLen;
        for (uint i = 0; i * 0x100 < len; i++) {
            lenLen++;
        }

        if (len <= 55) {
            encoded = new bytes(len+1);
            encoded[0] = byte(LIST_SHORT_START + len);

            assembly {
                encodedPtr := add(encoded, 0x21)
            }
            _memcpy(encodedPtr, selfPtr, len);
        } else {
            encoded = new bytes(1 + lenLen + len);
            encoded[0] = byte(LIST_LONG_START + lenLen - 1);

		    for (i = 1; i <= lenLen; i++) {
                encoded[i] = byte((len / (0x100**(lenLen - i))) % 0x100);
            }

            assembly {
                encodedPtr := add(add(encoded, 0x21), lenLen)
            }
            _memcpy(encodedPtr, selfPtr, len);
        }
        return encoded;
    }

    function _flatten(bytes[] memory self) private constant returns (bytes) {
        uint len;
        for (uint i = 0; i < self.length; i++) {
            len += self[i].length;
        }

        bytes memory flattened = new bytes(len);
        uint flattenedPtr;
        assembly {
            flattenedPtr := add(flattened, 0x20)
        }

        for (i = 0; i < self.length; i++) {
            bytes memory item = self[i];

            uint selfPtr;
            assembly {
                selfPtr := add(item, 0x20)
            }

            _memcpy(flattenedPtr, selfPtr, item.length);
            flattenedPtr += self[i].length;
        }
        return flattened;
    }

    /// This function is from Nick Johnson's string utils library
    function _memcpy(uint dest, uint src, uint len) private constant {
        // Copy word-length chunks while possible
        for(; len >= 32; len -= 32) {
            assembly {
                mstore(dest, mload(src))
            }
            dest += 32;
            src += 32;
        }

        // Copy remaining bytes
        uint mask = 256 ** (32 - len) - 1;
        assembly {
            let srcpart := and(mload(src), not(mask))
            let destpart := and(mload(dest), mask)
            mstore(dest, or(destpart, srcpart))
        }
    }
}
