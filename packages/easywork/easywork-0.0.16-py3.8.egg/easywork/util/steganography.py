from PIL import Image


def make_image_even(image):
    pixels = [(r >> 1 << 1, g >> 1 << 1, b >> 1 << 1, a >> 1 << 1) for r, g, b, a in image.getdata()]
    even_image = Image.new(image.mode, image.size)
    even_image.putdata(pixels)
    return even_image


def const_len_bin(size):
    return '0' * (8 - (len(bin(size)) - 2)) + bin(size).replace('0b', '')


def encode_image(path, data):
    image = Image.open(path)
    even_image = make_image_even(image)
    binary = ''.join(map(const_len_bin, bytearray(data, 'utf-8')))
    if len(binary) > len(image.getdata()) * 4:
        raise Exception(f'Can\'t encode more than {len(even_image.getdata()) * 4} bits in this image')
    encode_pixels = [(r + int(binary[i * 4 + 0]),
                      g + int(binary[i * 4 + 1]),
                      b + int(binary[i * 4 + 2]),
                      a + int(binary[i * 4 + 3]))
                     if i * 4 < len(binary) else (r, g, b, a) for i, (r, g, b, a)
                     in enumerate(list(even_image.getdata()))]
    even_image = Image.new(even_image.mode, even_image.size)
    even_image.putdata(encode_pixels)
    even_image.save(path)


def get_effective_binary(binary_part, zero_index):
    if not zero_index:
        return binary_part[1:]
    binary_list = []
    for i in range(zero_index):
        small_part = binary_part[8 * i: 8 * i + 8]
        binary_list.append(small_part[small_part.find('0') + 1:])
    return ''.join(binary_list)


def binary_to_string(binary):
    index = 0
    string = []
    while index + 1 < len(binary):
        zero_index = binary[index:].index('0')
        length = zero_index * 8 if zero_index else 8
        string.append(chr(int(get_effective_binary(binary[index: index + length], zero_index), 2)))
        index += length
    return ''.join(string)


def decode_image(path):
    image = Image.open(path)
    binary = ''.join([bin(r)[-1] + bin(g)[-1] + bin(b)[-1] + bin(a)[-1] for r, g, b, a in image.getdata()])
    many_zero_index = binary.find('0' * 16)
    end_index = many_zero_index + 8 - (many_zero_index % 8) if many_zero_index % 8 != 0 else many_zero_index
    return binary_to_string(binary[0:end_index])
