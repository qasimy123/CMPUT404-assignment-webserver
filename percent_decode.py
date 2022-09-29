'''
Attribution
Source: https://github.com/whatwg/url/blob/main/LICENSE
Title: URL Standard
Author: WHATWG
License: Creative Commons Attribution 4.0 International Public License
Link to License: https://github.com/whatwg/url/blob/main/LICENSE

Exact description of algorithm reproduced from the spec: https://url.spec.whatwg.org/#percent-encoded-bytes
'''


def percent_decode(input: bytes) -> str:
    '''
        Decodes a percent encoded string
    '''

    output = b''
    i = 0
    while i < len(input):
        # Algorithm for percent decoding as described in the spec
        if input[i] != 0x25:
            output += bytes([input[i]])
        elif i + 2 < len(input):
            if input[i+1] not in range(0x30, 0x39 + 1) and input[i+1] not in range(0x41, 0x46 + 1) and input[i+1] not in range(0x61, 0x66 + 1):
                output += bytes([input[i]])
            else:
                bytePoint = int(input[i+1:i+3], 16)
                output += bytes([bytePoint])
                i += 2
        i += 1
    return output.decode('utf-8')
