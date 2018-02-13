"""Some utils functions"""

import collections
import numpy as np
import torch as t
from sklearn.utils import shuffle


def get_train_valid_test(total, train, valid, test):
    """Returns three lists, containing train, validation and test indexes"""
    assert abs(train + valid + test - 1) < 1e-4, "The sum of the 2 proportions should be equal to 1 and was %s" % str(train + valid + test)
    indexes = shuffle(list(range(total)))
    train_indexes = indexes[:int(total * train)]
    valid_indexes = indexes[int(total * train):int(total * train) + int(total * valid)]
    test_indexes = indexes[int(total * train) + int(total * valid):]
    return train_indexes, valid_indexes, test_indexes


def categorical_cross_entropy_np(true_status, proba_pred, tol=1e-10):
    """
    Compute the categorical cross entropy between two 3d arrays
    :param true_status:
    :param proba_pred:
    :param tol:
    """
    results = []
    for status, proba in zip(true_status, proba_pred):
        modified_proba = ((proba == 0) * tol) + proba  # clipping
        results.append(np.mean(-1.0 * np.sum(np.log(modified_proba) * status, 1)))
    return np.mean(np.array(results))


def pad_sequences(sequences, maxlen=None, dtype='int32',
                  padding='pre', truncating='pre', value=0.):
    """Pads each sequence to the same length (length of the longest sequence).

    If maxlen is provided, any sequence longer
    than maxlen is truncated to maxlen.
    Truncation happens off either the beginning (default) or
    the end of the sequence.

    Supports post-padding and pre-padding (default).

    # Arguments
        sequences: list of lists where each element is a sequence
        maxlen: int, maximum length
        dtype: type to cast the resulting sequence.
        padding: 'pre' or 'post', pad either before or after each sequence.
        truncating: 'pre' or 'post', remove values from sequences larger than
            maxlen either in the beginning or in the end of the sequence
        value: float, value to pad the sequences to the desired value.

    # Returns
        x: numpy array with dimensions (number_of_sequences, maxlen)

    # Raises
        ValueError: in case of invalid values for `truncating` or `padding`,
            or in case of invalid shape for a `sequences` entry.
    """
    if not hasattr(sequences, '__len__'):
        raise ValueError('`sequences` must be iterable.')
    lengths = []
    for x in sequences:
        if not hasattr(x, '__len__'):
            raise ValueError('`sequences` must be a list of iterables. '
                             'Found non-iterable: ' + str(x))
        lengths.append(len(x))

    num_samples = len(sequences)
    if maxlen is None:
        maxlen = np.max(lengths)

    # take the sample shape from the first non empty sequence
    # checking for consistency in the main loop below.
    sample_shape = tuple()
    for s in sequences:
        if len(s) > 0:
            sample_shape = np.asarray(s).shape[1:]
            break

    x = np.array(num_samples*maxlen*[value]).reshape((num_samples, maxlen))
    for idx, s in enumerate(sequences):
        if not len(s):
            continue  # empty list/array was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError('Truncating type "%s" not understood' % truncating)

        # check `trunc` has expected shape
        trunc = np.asarray(trunc, dtype=dtype)
        if trunc.shape[1:] != sample_shape:
            raise ValueError('Shape of sample %s of sequence at position %s is different from expected shape %s' %
                             (trunc.shape[1:], idx, sample_shape))

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError('Padding type "%s" not understood' % padding)
    return x


def variable(array, requires_grad=False):
    """Wrapper for t.autograd.Variable"""
    if isinstance(array, np.ndarray):
        return t.autograd.Variable(t.from_numpy(array), requires_grad=requires_grad)
    elif isinstance(array, list) or isinstance(array,tuple):
        return t.autograd.Variable(t.from_numpy(np.array(array)), requires_grad=requires_grad)
    elif isinstance(array, float) or isinstance(array, int):
        return t.autograd.Variable(t.from_numpy(np.array([array])), requires_grad=requires_grad)
    elif isinstance(array, t.Tensor):
        return t.autograd.Variable(array, requires_grad=requires_grad)
    else: raise ValueError