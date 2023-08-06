from abc import ABC, abstractmethod
import inspect
import pickle

import numpy as np
from joblib import Parallel, delayed, cpu_count

from .channels import Channel
from .messages import unpack_to_bits, pack_to_dec, generate_data
from .encoders import PolarEncoder, Encoder, PolarWiretapEncoder
from .modulators import Modulator


def _logdomain_sum(x, y):
    if x < y:
        z = y + np.log1p(np.exp(x-y))
    else:
        z = x + np.log1p(np.exp(y-x))
    return z

def _logdomain_sum_multiple(x, y):
    _logpart = np.log1p(np.exp(-np.abs(x-y)))
    z = np.maximum(x, y) + _logpart
    return z


class Decoder(ABC):
    """Abstract decoder class."""
    def __init__(self, code_length, info_length, base=2, parallel=True):
        self.code_length = code_length
        self.info_length = info_length
        self.base = base
        self.parallel = parallel

    @abstractmethod
    def decode_messages(self, messages, channel=None): pass


class IdentityDecoder(Decoder):
    """Identity decoder. Simply returns the input."""
    @staticmethod
    def decode_messages(messages, channel=None):
        return messages


class RepetitionDecoder(Decoder):
    def __init__(self, *args, **kwargs): pass

    @staticmethod
    def decode_messages(messages, channel=None):
        decoded = np.zeros((len(messages), 1))
        for idx, message in enumerate(messages):
            val, counts = np.unique(message, return_counts=True)
            _decision = np.argmax(counts)
            decoded[idx] = val[_decision]
        return decoded


class LinearDecoder(Decoder):
    """Linear block decoder.

    Parameters
    ----------
    TODO
    """
    def decode_messages(self, messages, channel=None):
        raise NotImplementedError()


class PolarDecoder(Decoder):
    """Polar code decoder. Taken from **polarcodes.com**

    The decoder for BAWGN channels expects a channel output of noisy codewords
    which are modulated to +1 and -1.

    Parameters
    ----------
    code_length : int
        Length of the code.

    info_length : int
        Length of the messages.

    design_channel : str or Channel
        Name of the used channel. Valid choices are currently "BAWGN" and "BSC".

    design_channelstate : float, optional
        State of the design channel. For "BAWGN" channels, this corresponds to
        the SNR value in dB. For "BSC" channels, this corresponds to the
        bit-flip probability.

    pos_lookup : array, optional
        Position lookup of the polar code, where -1 indicates message bits,
        while 0 and 1 denote the frozenbits.

    frozenbits : array, optional
        Bits used for the frozen bit positions. This is ignored, if `pos_lookup`
        is provided.

    parallel : bool, optional
        If True, parallel processing is used. This might not be available on
        all machines and causes higher use of system resources.
    """
    def __init__(self, code_length, info_length, design_channel,
                 design_channelstate=0., pos_lookup=None, frozenbits=None,
                 parallel=True, **kwargs):
        if isinstance(design_channel, Channel):
            channel_name = design_channel.name
            design_channelstate = design_channel.get_channelstate()
        else:
            channel_name = design_channel
        self.design_channel = channel_name
        self.design_channelstate = design_channelstate
        if pos_lookup is None:
            self.pos_lookup = PolarEncoder.construct_polar_code(
                code_length, info_length, design_channel, design_channelstate,
                frozenbits)
        else:
            self.pos_lookup = np.array(pos_lookup)
        self.rev_index = self._reverse_index(code_length)
        self.idx_first_one = self._index_first_num_from_msb(code_length, 1)
        self.idx_first_zero = self._index_first_num_from_msb(code_length, 0)
        super().__init__(code_length, info_length, parallel=parallel)

    @staticmethod
    def _reverse_index(code_length):
        _n = int(np.ceil(np.log2(code_length)))
        rev_idx = [pack_to_dec(np.flip(unpack_to_bits([idx], _n), axis=1))[0][0]
                   for idx in range(code_length)]
        return rev_idx

    @staticmethod
    def _index_first_num_from_msb(code_length, number):
        _n = int(np.ceil(np.log2(code_length)))
        idx_list = np.zeros(code_length)
        for idx in range(code_length):
            idx_bin = unpack_to_bits([idx], _n)[0]
            try:
                last_level = np.where(idx_bin == number)[0][0]
            except IndexError:
                last_level = _n-1
            idx_list[idx] = last_level
        return idx_list

    def decode_messages(self, messages, channel=None):
        """Decode polar encoded messages.

        Parameters
        ----------
        messages : array
            Array of received (noisy) codewords which were created by polar
            encoding messages. Each row represents one received word.

        channel : float or Channel, optional
            This can either be a channel state, e.g., SNR in an AWGN channel, 
            of the channel model used for constructing the decoder  or a
            `channels.Channel` object.
            If None, the design parameters are used.

        Returns
        -------
        decoded_messages : array
            Array containing the estimated messages after decoding the channel
            output.
        """
        #decoded = np.zeros((len(messages), self.info_length))
        decoded = np.zeros((len(messages), self.code_length))
        channel_name = self.design_channel
        if channel is None:
            channel_state = self.design_channelstate
        elif isinstance(channel, Channel):
            channel_name = channel.name
            if channel_name != self.design_channel:
                Warning("The channel you passed for decoding ('{}') is different "
                        "to the one you used for constructing the decoder ('{}')!"
                        .format(channel_name, self.design_channel))
            channel_state = channel.get_channelstate()
        else:
            channel_state = channel
        if channel_name == "BAWGN":
            snr = 10**(channel_state/10.)
            initial_llr = -2*np.sqrt(2*(self.info_length/self.code_length)*snr)*messages
            #if self.parallel:
            #    num_cores = cpu_count()
            #    decoded = Parallel(n_jobs=num_cores)(
            #        delayed(self._polar_llr_decode)(k) for k in initial_llr)
            #    decoded = np.array(decoded)
            #else:
            #    for idx, _llr_codeword in enumerate(initial_llr):
            #        decoded[idx] = self._polar_llr_decode(_llr_codeword)
            decoded = self._polar_llr_decode_multiple(initial_llr)
        elif channel_name == "BSC":
            llr = np.log(channel_state) - np.log(1-channel_state)
            initial_llr = (2*messages - 1) * llr
            if self.parallel:
                num_cores = cpu_count()
                decoded = Parallel(n_jobs=num_cores)(
                    delayed(self._polar_llr_decode)(k) for k in initial_llr)
                decoded = np.array(decoded)
            else:
                for idx, _llr_codeword in enumerate(initial_llr):
                    decoded[idx] = self._polar_llr_decode(_llr_codeword)
        decoded = self._get_info_bit_positions(decoded)
        return decoded

    def _get_info_bit_positions(self, decoded):
        return decoded[:, self.pos_lookup == -1]

    def _polar_llr_decode(self, initial_llr):
        llr = np.zeros(2*self.code_length-1)
        llr[self.code_length-1:] = initial_llr
        bit_branch = np.zeros((2, self.code_length-1))
        decoded = np.zeros(self.code_length)
        for j in range(self.code_length):
            rev_idx = self.rev_index[j]
            llr = self._update_llr(llr, bit_branch, rev_idx)
            if self.pos_lookup[rev_idx] <= -1:
                if llr[0] > 0:
                    decoded[rev_idx] = 0
                else:
                    decoded[rev_idx] = 1
            else:
                decoded[rev_idx] = self.pos_lookup[rev_idx]
            bit_branch = self._update_bit_branch(decoded[rev_idx], rev_idx, bit_branch)
        #return decoded[self.pos_lookup == -1]
        return decoded

    def _update_llr(self, llr, bit_branch, rev_idx):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == 0:
            next_level = _n
        else:
            last_level = int(self.idx_first_one[rev_idx]+1)
            st = int(2**(last_level-1))
            ed = int(2**(last_level)-1)
            for idx in range(st-1, ed):
                llr[idx] = self._lowerconv(
                    bit_branch[0, idx], llr[ed+2*(idx+1-st)], llr[ed+2*(idx+1-st)+1])
            next_level = last_level - 1
        for level in np.arange(next_level, 0, -1):
            st = int(2**(level-1))
            ed = int(2**(level) - 1)
            for idx in range(st-1, ed):
                llr[idx] = self._upperconv(llr[ed+2*(idx+1-st)], llr[ed+2*(idx+1-st)+1])
        return llr

    @staticmethod
    def _lowerconv(upper_decision, upper_llr, lower_llr):
        if upper_decision == 0:
            llr = lower_llr + upper_llr
        else:
            llr = lower_llr - upper_llr
        return llr

    @staticmethod
    def _upperconv(llr1, llr2):
        llr = _logdomain_sum(llr1+llr2, 0) - _logdomain_sum(llr1, llr2)
        return llr

    def _update_bit_branch(self, bit, rev_idx, bit_branch):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == self.code_length-1:
            return
        elif rev_idx < self.code_length/2:
            bit_branch[0, 0] = bit
        else:
            last_level = int(self.idx_first_zero[rev_idx]+1)
            bit_branch[1, 0] = bit
            for level in range(1, last_level-2+1):
                st = int(2**(level-1))
                ed = int(2**(level)-1)
                for idx in range(st-1, ed):
                    bit_branch[1, ed+2*(idx+1-st)] = np.mod(bit_branch[0, idx]+bit_branch[1, idx], 2)
                    bit_branch[1, ed+2*(idx+1-st)+1] = bit_branch[1, idx]
            level = last_level-1
            st = int(2**(level-1))
            ed = int(2**(level)-1)
            for idx in range(st-1, ed):
                bit_branch[0, ed+2*(idx+1-st)] = np.mod(bit_branch[0, idx]+bit_branch[1, idx], 2)
                bit_branch[0, ed+2*(idx+1-st)+1] = bit_branch[1, idx]
        return bit_branch

#####
    def _polar_llr_decode_multiple(self, initial_llr):
        llr = np.zeros((len(initial_llr), 2*self.code_length-1))
        llr[:, self.code_length-1:] = initial_llr
        bit_branch = np.zeros((len(initial_llr), 2, self.code_length-1))
        decoded = np.zeros((len(initial_llr), self.code_length))
        for j in range(self.code_length):
            rev_idx = self.rev_index[j]
            llr = self._update_llr_multiple(llr, bit_branch, rev_idx)
            if self.pos_lookup[rev_idx] <= -1:
                #decoded[:, rev_idx] = 0
                _idx = np.where(llr[:, 0] <= 0)[0]
                decoded[_idx, rev_idx] = 1
            else:
                decoded[:, rev_idx] = self.pos_lookup[rev_idx]
            bit_branch = self._update_bit_branch_multiple(
                decoded[:, rev_idx], rev_idx, bit_branch)
        #return decoded[self.pos_lookup == -1]
        return decoded

    def _update_llr_multiple(self, llr, bit_branch, rev_idx):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == 0:
            next_level = _n
        else:
            last_level = int(self.idx_first_one[rev_idx]+1)
            st = int(2**(last_level-1))
            ed = int(2**(last_level)-1)
            for idx in range(st-1, ed):
                llr[:, idx] = self._lowerconv_multiple(
                    bit_branch[:, 0, idx], llr[:, ed+2*(idx+1-st)], llr[:, ed+2*(idx+1-st)+1])
            next_level = last_level - 1
        for level in np.arange(next_level, 0, -1):
            st = int(2**(level-1))
            ed = int(2**(level) - 1)
            for idx in range(st-1, ed):
                llr[:, idx] = self._upperconv_multiple(
                    llr[:, ed+2*(idx+1-st)], llr[:, ed+2*(idx+1-st)+1])
        return llr

    def _update_bit_branch_multiple(self, bit, rev_idx, bit_branch):
        _n = int(np.ceil(np.log2(self.code_length)))
        if rev_idx == self.code_length-1:
            return
        elif rev_idx < self.code_length/2:
            bit_branch[:, 0, 0] = bit
        else:
            last_level = int(self.idx_first_zero[rev_idx]+1)
            bit_branch[:, 1, 0] = bit
            for level in range(1, last_level-2+1):
                st = int(2**(level-1))
                ed = int(2**(level)-1)
                for idx in range(st-1, ed):
                    bit_branch[:, 1, ed+2*(idx+1-st)] = np.mod(bit_branch[:, 0, idx]+bit_branch[:, 1, idx], 2)
                    bit_branch[:, 1, ed+2*(idx+1-st)+1] = bit_branch[:, 1, idx]
            level = last_level-1
            st = int(2**(level-1))
            ed = int(2**(level)-1)
            for idx in range(st-1, ed):
                bit_branch[:, 0, ed+2*(idx+1-st)] = np.mod(bit_branch[:, 0, idx]+bit_branch[:, 1, idx], 2)
                bit_branch[:, 0, ed+2*(idx+1-st)+1] = bit_branch[:, 1, idx]
        return bit_branch

    @staticmethod
    def _lowerconv_multiple(upper_decision, upper_llr, lower_llr):
        llr = lower_llr - upper_llr
        idx = np.where(upper_decision == 0)
        llr[idx] = lower_llr[idx] + upper_llr[idx]
        return llr

    @staticmethod
    def _upperconv_multiple(llr1, llr2):
        llr = _logdomain_sum_multiple(llr1+llr2, 0) - _logdomain_sum_multiple(llr1, llr2)
        return llr
####

class PolarWiretapDecoder(PolarDecoder):
    """Decoder class for decoding polar wiretap codes.
    You can either provide both channels (to Bob and Eve) or provide the main
    channel to Bob and the position lookup of the already constructed code.

    Parameters
    ----------
    code_length : int
        Length of the codewords.

    design_channel_bob : str
        Channel name of the main channel to Bob. Valid choices are the channel
        models which are supported by the PolarDecoder.

    design_channel_eve : str, optional
        Channel name of the side channel to Eve. Valid choices are the channel
        models which are supported by the PolarEncoder.

    design_channelstate_bob : float, optional
        Channelstate of the main channel.

    design_channelstate_eve : float, optional
        Channelstate of the side channel.

    pos_lookup : array, optional
        Position lookup of the constructed wiretap code. If this is provided,
        no additional code is constructed and the values of Eve's channel are
        ignored.
    """
    def __init__(self, code_length, design_channel_bob, design_channel_eve=None,
                 design_channelstate_bob=0, design_channelstate_eve=0.,
                 pos_lookup=None, frozenbits=None, parallel=True, 
                 info_length_bob=None, random_length=None, **kwargs):
        if pos_lookup is None:
            pos_lookup = PolarWiretapEncoder.construct_polar_wiretap_code(
                code_length, design_channel_bob, design_channel_eve,
                design_channelstate_bob, design_channelstate_eve, frozenbits,
                info_length_bob, random_length)
        info_length = np.count_nonzero(pos_lookup == -1)
        info_length_bob = np.count_nonzero(pos_lookup < 0)
        super().__init__(code_length, info_length, design_channel_bob,
                 design_channelstate=design_channelstate_bob,
                 pos_lookup=pos_lookup, frozenbits=frozenbits,
                 parallel=parallel, **kwargs)
