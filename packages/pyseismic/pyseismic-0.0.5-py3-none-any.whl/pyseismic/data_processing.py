import numpy as np


def read_bin(path, shape=None):
    if not shape:
        shape = get_shape(path)
    dat = np.fromfile(path, dtype='float32')
    dat = np.reshape(dat, shape)
    return dat


def write_bin(data, fn):
    data = np.array(data, dtype='float32')
    suffix = shape2str(data.shape)
    if fn[-4:] == '.bin':
        fn = fn[-4:]
    data.tofile(f'{fn}_{suffix}.bin')


def shape2str(x):
    # (1, 2) --> '1x2'
    s = ''
    for i in x:
        s = s + 'x' + str(i)
    return s[1:]


def get_shape(fname):
    # 'xxx_5x3.bin' --> (5, 3)
    fname_len = len(fname)
    fname_inverse = fname[::-1]
    width_right = fname.find('.bin')
    depth_left = fname_len - fname_inverse.find('_')
    shape = tuple(map(int, fname[depth_left:width_right].split('x')))
    return shape
