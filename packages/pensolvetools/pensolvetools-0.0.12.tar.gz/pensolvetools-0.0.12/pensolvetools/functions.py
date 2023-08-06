import numpy as np


def small(x, n):
    a = np.sort(x)
    return a[n-1]


def large(x, n):
    a = np.sort(x)[::-1]
    return a[n-1]


def linest(ys, xs, const=True, stats=False):
    if const:
        return np.array(np.mean(ys / xs))  # This may not be correct?
    else:
        return np.polyfit(xs, ys, 1)


def geomean(x):
    a = np.log(x)
    return np.exp(a.sum()/len(a))


def match(x0, x, match_type=1):
    if match_type == 0:
        return np.where(np.array(x) == x0)[0][0].item()
    elif match_type == -1:
        return len(x) - np.searchsorted(np.array(x)[::-1], x0, side="left")
    elif match_type == 1:
        return np.searchsorted(x, x0, side="right") - 1


def clean_params_for_sum_fns(params):
    p_all = []
    for param in params:
        if hasattr(param, "__len__"):
            if hasattr(param, 'size') and param.size == 1:
                param = [np.asscalar(param)]
            pnew = [p for p in param if not isinstance(p, str)]
            p_all += pnew
        elif not isinstance(param, str):
            p_all += [param]
    if not len(p_all):
        return None
    return p_all


def clean_params_for_eval_fns(params):
    # TODO: this is tricky because it is used to handle repeated expressions, but also MAX across single values and lists
    # TODO: to remedy could include an output_len parameter, where if it is repating then output should have len.
    n = None
    for param in params:
        if hasattr(param, "__len__") and not isinstance(param, str):
            if hasattr(param, 'size') and param.size == 1:
                continue  # scalar array
            if n is not None and n != len(param):
                raise ValueError("Cannot evaluate fn with different length args")
            n = len(param)
    p_all = []
    for param in params:
        if isinstance(param, str):
            continue
        if hasattr(param, "__len__"):
            if hasattr(param, 'size') and param.size == 1:
                if n is not None:
                    param = [np.asscalar(param)] * n
                else:
                    param = [np.asscalar(param)]
            pnew = [p for p in param if not isinstance(p, str)]
            p_all.append(pnew)
        else:
            if n is not None:
                p_all.append([param] * n)
            else:
                p_all.append([param])
    if not len(p_all):
        return None
    return np.array(p_all)


def p_max(params):
    p_all = clean_params_for_eval_fns(params)
    if p_all is None:
        return None
    if len(np.shape(p_all)) > 1 and np.shape(p_all)[1] > 1:
        return np.max(p_all, axis=0)
    else:
        return np.max(p_all)


def p_min(params):
    p_all = clean_params_for_eval_fns(params)
    if p_all is None:
        return None
    if len(np.shape(p_all)) > 1 and np.shape(p_all)[1] > 1:
        return np.min(p_all, axis=0)
    else:
        return np.min(p_all)


def p_sum(params):
    p_all = clean_params_for_sum_fns(params)
    return None if p_all is None else sum(p_all)


def lookup(x, x0, y, approx=True):
    """
    Equivalent to the spreadsheet LOOKUP,
    but supports the approx option like VLOOKUP

    :param x:
    :param x0:
    :param y:
    :param approx:
    :return:
    """
    if isinstance(x[0], str):
        x0 = str(x0)
    if not approx:  # need exact match
        return y[np.where(x0 == np.array(x))[0][0]]
    else:
        inds = np.searchsorted(x, x0, side='right') - 1
        return y[inds]


def vlookup(x0, vals, ind, approx=True):
    """
    Equivalent to the spreadsheet VLOOKUP function

    :param vals: array_like
        2d array of values - first column is searched for index
    :param x0:
    :param ind:
    :param approx:
    :return:
    """
    if isinstance(vals[0][0], str):
        x0 = str(x0)
    if not approx:  # need exact match
        return vals[int(ind)][np.where(x0 == np.array(vals[0]))[0][0]]
    else:
        inds = np.searchsorted(vals[0], x0, side='right') - 1
        return vals[ind][int(inds)]


# def lookup(x0, x, y=None):  # TODO: delete
#     if y is None:
#         y = x
#     inds = np.searchsorted(x, x0, side='right') - 1
#     return y[inds]


def p_or(*args):
    if len(args) != 2:
        return np.logical_or.reduce(np.array(args))
    return np.logical_or(*args)


def p_and(*args):
    if len(args) != 2:
        return np.logical_and.reduce(np.array(args))
    return np.logical_and(*args)


def concat(parts):
    if isinstance(parts[0], (list, np.ndarray)):
        max_len = len(parts[0])
        for i, part in enumerate(parts):
            if not isinstance(parts[i], (list, np.ndarray)):
                parts[i] = [part] * max_len
        new_list = []
        for i in range(len(parts[0])):
            sub_list = []
            for j in range(len(parts)):
                sub_list.append(str(parts[j][i]))
            new_list.append(''.join(sub_list))
        return new_list
    return ''.join([str(x) for x in parts])


class SheetObj(object):
    pass
