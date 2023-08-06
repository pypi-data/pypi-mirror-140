from math import ceil

from nbt.chunk import block_id_to_name


class Section(object):

    def __init__(self, nbt, version):
        self.names = []
        self.indexes = []

        # Is the section flattened ?
        # See https://minecraft.gamepedia.com/1.13/Flattening

        if version == 0 or version == 1343:  # 1343 = MC 1.12.2
            self._init_array(nbt)
        elif 1631 <= version <= 2230:  # MC 1.13 to MC 1.15.2
            self._init_index_unpadded(nbt)
        elif 2566 <= version <= 2730:  # MC 1.16.0 to MC 1.17.2 (latest tested version)
            self._init_index_padded(nbt)
        else:
            self._init_index_padded_1_18(nbt)

        # Section contains 4096 blocks whatever data version
        assert len(self.indexes) == 4096

    # Decode legacy section
    # Contains an array of block numeric identifiers
    def _init_array(self, nbt):
        bids = []
        for bid in nbt['Blocks'].value:
            try:
                i = bids.index(bid)
            except ValueError:
                bids.append(bid)
                i = len(bids) - 1
            self.indexes.append(i)

        for bid in bids:
            bname = block_id_to_name(bid)
            self.names.append(bname)

    # Decode modern section
    # Contains palette of block names and indexes packed with run-on between elements (pre 1.16 format)
    def _init_index_unpadded(self, nbt):
        for p in nbt['Palette']:
            name = p['Name'].value
            self.names.append(name)

        states = nbt['BlockStates'].value

        # Block states are packed into an array of longs
        # with variable number of bits per block (min: 4)
        num_bits = (len(self.names) - 1).bit_length()
        if num_bits < 4: num_bits = 4
        assert num_bits == len(states) * 64 / 4096
        mask = pow(2, num_bits) - 1

        i = 0
        bits_left = 64
        curr_long = states[0]

        for _ in range(0, 4096):
            if bits_left == 0:
                i = i + 1
                curr_long = states[i]
                bits_left = 64

            if num_bits <= bits_left:
                self.indexes.append(curr_long & mask)
                curr_long = curr_long >> num_bits
                bits_left = bits_left - num_bits
            else:
                i = i + 1
                next_long = states[i]
                remaining_bits = num_bits - bits_left

                next_long = (next_long & (pow(2, remaining_bits) - 1)) << bits_left
                curr_long = (curr_long & (pow(2, bits_left) - 1))
                self.indexes.append(next_long | curr_long)

                curr_long = states[i]
                curr_long = curr_long >> remaining_bits
                bits_left = 64 - remaining_bits

    # Decode modern section
    # Contains palette of block names and indexes packed with padding if elements don't fit (post 1.16 format)
    def _init_index_padded(self, nbt):
        for p in nbt['Palette']:
            name = p['Name'].value
            self.names.append(name)

        states = nbt['BlockStates'].value
        num_bits = (len(self.names) - 1).bit_length()
        if num_bits < 4: num_bits = 4
        mask = 2 ** num_bits - 1

        indexes_per_element = 64 // num_bits
        last_state_elements = 4096 % indexes_per_element
        if last_state_elements == 0: last_state_elements = indexes_per_element

        assert len(states) == ceil(4096 / indexes_per_element)

        for i in range(len(states) - 1):
            long = states[i]

            for _ in range(indexes_per_element):
                self.indexes.append(long & mask)
                long = long >> num_bits

        long = states[-1]
        for _ in range(last_state_elements):
            self.indexes.append(long & mask)
            long = long >> num_bits

    def get_block(self, x, y, z):
        # Blocks are stored in YZX order
        i = y * 256 + z * 16 + x
        p = self.indexes[i]
        return self.names[p]

    def iter_block(self):
        for i in range(0, 4096):
            p = self.indexes[i]
            yield self.names[p]
