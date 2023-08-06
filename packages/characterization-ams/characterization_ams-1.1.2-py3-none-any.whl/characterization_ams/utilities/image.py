import os
import struct
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from characterization_ams.utilities import calc
from characterization_ams.utilities import utilities as ut


def histogram(df,
              bin=1,
              ):
    """
    Thin wrapper for numpy.histogram to return as pandas.DataFrame for
    plotting purposes
    """
    import pdb
    pdb.set_trace()
    im = df.stack()
    max_ = bin * np.ceil(im.max() / bin)
    #max_value = bin * np.ceil(float(im.stack().max()) / bin)

    count, divisions = np.histogram(im,
                                    range=(0, max_),
                                    bins=int(np.ceil(max_ / bin)))

    #return count, divisions
    #divisions += offset
    count = np.append(count, [0])
    #region, region_desc = roi_get(im)
    out = pd.DataFrame({'DN': divisions,
                        'Counts': count})

    # temp['1-CDF'] = calc.cdf(temp['Counts'])

    """
        im = im[dfutils.int_cols(im)]
        max_value = bin * np.ceil(float(im.stack().max()) / bin)
        count, divisions = np.histogram(im.stack(),
                                        range=(-offset, max_value + offset),
                                        bins=int(np.ceil(max_value / bin)+1))
        divisions += offset
        count = np.append(count, [0])
        region, region_desc = roi_get(im)
        temp = pd.DataFrame({'Color': color,
                             'DN': divisions,
                             'Region': region,
                             'RegionDesc': region_desc,
                             'Counts': count})
        temp['1-CDF'] = calc.cdf(temp['Counts'])
        data = pd.concat([data, temp])
    """

    return out


def implot(df,
           clim=['-3s', '3s'],
           oor=('-3.5s', '3.5s'),
           vlim=('min', 'max'),
           slim=(-5.5, 5.5),
           cmap='viridis',
           oormarks=False,
           layout='vertical',
           rectim=None,
           rectsig=None,
           vscale='linear',
           figkwargs: dict = None,
           sigkwargs: dict = None,
           imkwargs: dict = None,
           debug: bool = False,
           **kwargs
           ):
    """
    Render image and normal quantile (cdf) plot

    Args:
       df (pandas.DataFrame|str):  file path (passed to imread)
                                   or DataFrame containing pixel data

    Keyword Args:
        clim (tuple of aggfuns, ('-3s', '3s')): color limits (color scale)
        oor (tuple of aggfuns, ('-3.5s', '3.5s')): out of range limit
                                                  (outlier marking)
        vlim (tuple of aggfuns, ('min', 'max')): value limits (x-axis)
        slim (tuple of aggfuns, (-5.2, 5.2)): sigma limits (y-axis)
        cmap (str, viridis): matplotlib colormap
        oormarks (bool, False): render OOR pixels on image as embiggened marks
        layout (str, 'vertical'): axes vertically oriented else horizontal
        rectim (list of numeric): image rectangle args
        rectsig (list of numeric): sigma normal rectangle args
        figkwargs (dict, None): figure kwargs
        sigkwargs (dict, None): sigma axes kwargs
        imkwargs (dict, None): image axes kwargs

        other *kwargs* passed directly to ``imread``

    Returns
        fig (matplotlib.Figure): figure instance

    """

    figkwargs = {} if figkwargs is None else figkwargs
    sigkwargs = {} if sigkwargs is None else sigkwargs
    imkwargs = {} if imkwargs is None else imkwargs

    figkwargs.setdefault('facecolor', 'w')

    im = df if isinstance(df, pd.DataFrame) else pd.DataFrame(df)
    imflat = pd.Series(im.values.flatten())
    imflat = imflat[imflat.notnull()]
    nq = calc.normal_quantile(imflat)

    oor = calc.limits(oor, imflat)
    clim = calc.limits(clim, imflat)
    vlim = calc.limits(vlim, imflat)
    slim = calc.limits(slim, imflat)

    # oor can't overlap clim
    oor[0] == clim[0] if oor[0] > clim[0] else oor[0]
    oor[1] == clim[1] if oor[1] < clim[1] else oor[1]

    imth, xyl = threshold(im, thresh=oor[0], fun=np.less)
    imtl, xyh = threshold(im, thresh=oor[1], fun=np.greater)

    colors = np.linspace(0, 1, 256)
    colors = np.vstack((colors, colors))

    try:  # this stupidness likely fixed in mpl 2.0
        locol = plt.cm.get_cmap(cmap).colors[0]
        hicol = plt.cm.get_cmap(cmap).colors[-1]

    except Exception:
        hicol = plt.cm.get_cmap(cmap, 2)(1)[:3]
        locol = plt.cm.get_cmap(cmap, 2)(0)[:3]

    fig = plt.figure(**figkwargs)

    if layout == 'vertical':
        rectim = rectim or [0.05, 0.5, 0.9, 0.5]
        rectsig = rectsig or [0.2, 0.1, 0.6, 0.35]

    else:
        rectim = rectim or [0.5, 0.05, 0.4, 0.9]
        rectsig = rectsig or [0.05, 0.15, 0.4, 0.8]

    axs = [fig.add_axes(rectsig, **sigkwargs), fig.add_axes(rectim, **imkwargs)]

    if cmap == 'gray':
        oorcols = ((0., 0., 0.8), (0.8, 0.0, 0.0))
    else:
        oorcols = ((0., 0., 0.), (0.8, 0.0, 0.0))

    oorlkws = dict(marker='s', markersize=3,
                   color=oorcols[0], alpha=1, linestyle=''
                   )
    oorhkws = dict(marker='s', markersize=3, markeredgecolor=oorcols[1],
                   color=oorcols[1], alpha=1, linestyle='')

    if oormarks:
        axs[1].plot(xyl.col, xyl.row, **oorlkws)
        axs[1].plot(xyh.col, xyh.row, **oorhkws)

    axs[1].imshow(im, cmap=cmap, interpolation='none', aspect='equal', clim=clim)
    axs[1].grid(False, which='both', axis='both')
    axs[1].yaxis.tick_right()

    # set some colors and transparency of fills
    alphaim = 0.6
    alphaoor = alphaim

    # render main colorbar with continuous colormap
    axs[0].imshow(colors, aspect='auto', extent=(*clim, *slim),
                  cmap=cmap, alpha=alphaim)

    # render colorbar between bottom of colormap and the "oor" lo limit with the same
    # color as bottom of colormap
    axs[0].fill_between([oor[0], clim[0]], *slim, color=locol, alpha=alphaim, zorder=0)

    # render colorbar between top of colormap and the "oor" high limit with the same
    # color as top of colormap
    axs[0].fill_between([clim[1], oor[1]], *slim, color=hicol, alpha=alphaim, zorder=0)

    # render from the value (x-axis) low limit to the oor low point with the oorlo color
    axs[0].fill_between([vlim[0], oor[0]], *slim, color=oorcols[0], alpha=alphaoor, zorder=0)

    # render from the value (x-axis) high limit to the oor low point with the oorhi color
    axs[0].fill_between([oor[1], vlim[1]], *slim, color=oorcols[1], alpha=alphaoor, zorder=0)

    # sigma normal grid
    vlw = 1
    alphav = 0.8
    axs[0].vlines(oor[0], *slim, lw=vlw,  color='k', linestyle='--', alpha=alphav)
    axs[0].vlines(oor[1], *slim, lw=vlw,  color='k', linestyle='--', alpha=alphav)
    axs[0].vlines(clim[0], *slim, lw=vlw, color='k', linestyle='--',  alpha=alphav)
    axs[0].vlines(clim[1], *slim, lw=vlw, color='k', linestyle='--',  alpha=alphav)

    axs[0].set(xlim=vlim, yticks=np.linspace(-6.0, 6.0, 13),
               ylim=slim, ylabel='$\sigma_{normal}$', xlabel='$DN$',
               facecolor='w')

    #axs[0].xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())  # how to find maj/2?
    axs[0].yaxis.set_minor_locator(mpl.ticker.MultipleLocator(0.5))

    mgcol = '#cccccc'
    axs[0].grid(True, 'major', axis='both', lw=2,
                color=mgcol, linestyle=':', alpha=1.0)
    #axs[0].grid(True, 'minor', axis='both', lw=0.50, color=np.ones(3), linestyle='-', alpha=0.7)

    axs[0].hlines(0, *vlim, mgcol, lw=5)
    axs[0].plot(nq.X, nq.Sigma, color=0.5 * np.ones(3), lw=4, zorder=1e6)

    axs[0].set_xscale(vscale)

    lims = (f'clim=({clim[0]:0.0f},{clim[1]:0.0f}) '
            f'oor=({oor[0]:0.0f},{oor[1]:0.0f}) '
            f'slim=({slim[0]:0.1f},{slim[1]:0.1f})')
            #f'vlim=({vlim[0]:0.0f},{vlim[1]:0.1f}) '


    fig.text(0.01, 0.00, lims)

    if not mpl.pyplot.isinteractive():
        return fig


def load_ip(name, as_dataframe=False):
    """
    Read ip image file. Note this function uses python native and numpy modules only
    so works in all OSs.

    Adapted from function written by Victor Foerster

    Args:
        name: .ip image file

    Keyword Args:
        as_dataframe(bool, False): if True return as pandas.Dataframe,
            else numpy.array

    Returns:
        img (pandas.DataFrame | numpy.array): image data
    """

    with open(name, "rb") as fhandle:
        fhandle.seek(4)
        typ = struct.unpack('<h', fhandle.read(2))[0]
        fhandle.seek(8)
        width = struct.unpack('<h', fhandle.read(2))[0]
        fhandle.seek(12)
        height = struct.unpack('<h', fhandle.read(2))[0]
    if typ == 0:
        img = np.fromfile(name, dtype=np.uint16)
        img = np.reshape(img[8:8 + width * height], (height, width))
    elif typ == 1:
        img = np.fromfile(name, dtype=np.uint32)
        img = np.reshape(img[4:4 + width * height], (height, width))
    elif typ == 2:
        img = np.fromfile(name, dtype=np.float32)
        img = np.reshape(img[4:4 + width * height], (height, width))
    else:
        raise Exception('idp type {} not implemented'.format(typ))

    return pd.DataFrame(img) if as_dataframe else img


def stats(df,
          meta=None,
          aggs=None,
          sigma=None,
          tail=3,
          step_tail=0.1,
          step_inner=0.5,
          **kwargs
          ):
    """
    Calculate image statistics

    Args:
        df (pandas.Dataframe or np.array): array or DataFrame of image data

    Keyword Args:
        meta (pandas.Series, None): metadata to merge with calculated stats
        aggs (list of aggs|"normal_quantile"): alias for aggregation function
        sigma (numeric, None): min|max sigma value
        tail (numeric, 3): point at which to use the step_tail spacing
        step_tail (numeric, 0.2): tail sigma spacing
        step_inner (numberic, 0.5): intermediate sigma spacing

    Returns:
        data (pandas.DataFrame): calculated quantile data

    .. note:: aggs is passed directly to `calc.aggfuns`_ (see for more details)

    .. note:: need to decompose planes prior to calling if desired

    """

    values = df.values.flatten() if isinstance(df, pd.DataFrame) \
                                 else df.flatten()

    if aggs == 'normal_quantile':
        stats = calc.normal_quantile(values).rename(columns={'X': 'Value'})

    else:
        if aggs is None:
            if sigma is None:
                n = len(values)
                sig = abs(calc.ss.norm.ppf(1/n))
                # sigma = np.round(np.trunc(sig * 10) / 10)
                sigma = np.ceil(sig * 1 / step_tail) / (1 / step_tail)

            aggs = np.arange(-sigma, -tail, step_tail).tolist() + \
                   np.arange(-tail, tail, step_inner).tolist() + \
                   np.arange(tail, sigma+1e-9, step_tail).tolist()
            n_decimals = ut.num_decimals(step_tail)
            if n_decimals is not None:
                aggs = np.around(aggs, n_decimals)
            aggs = sorted(list(set(aggs)))

            # get the minimum precision required for nice printing
            n_decimals = 1 if not n_decimals else n_decimals # use at least one
            prec_tail = len(str(step_tail-int(step_tail))[1:].strip('.'))
            prec_inner = len(str(step_inner-int(step_inner))[1:].strip('.'))
            prec_max = prec_tail if prec_tail > prec_inner else prec_inner
            n_decimals = prec_max if prec_max > n_decimals else n_decimals

            fmt_ = '{:0.%df}S' % n_decimals
            aggs = [fmt_.format(s) for s in aggs]
            aggs = [aggs[0]] + \
                   [x for i, x in enumerate(aggs[1:])
                    if x != aggs[i-1]]

        stats = pd.DataFrame(calc.aggfuns(aggs, values,
                             fast_q=True)).reset_index()
        stats.columns = ['Stat', 'Value']

        stats['Sigma'] = stats.Stat.map(calc.aggsigma_to_float)
        try:
            stats.loc[stats.Sigma > 0, 'Stat'] = \
                '+' + stats.loc[stats.Sigma > 0, 'Stat'].map(str)

            stats = stats.sort_values('Sigma')
        except Exception:  # doesn't work with mean, std, etc
            pass

    if meta is not None:
        stats = stats.join(pd.DataFrame(data=[meta] * len(stats),
                                        index=stats.index))

    return stats


def threshold(df, thresh=7000, fun=np.greater):
    """
    Threshold image DataFrame returning only rows/columns with OOR values
    as well as a list of (row, col)

    Args:
       df (pandas.DataFrame):  DataFrame containing pixel data

    Keyword args:
        thresh (numeric): threshold value
        fun (callable): function that accepts a DataFrame, thresh
                        as the first and second parameters

    Returns:
        df (pandas.DataFrame): DataFrame with only OOR values
        rowcol (pandas.DataFrame): DataFrame with row, col columns of
                                   OOR values

    """
    # gt or lt ...
    imt = df[fun(df, thresh)].dropna(how='all').dropna(how='all', axis=1)

    # nice pandas way to get this?
    rc = []
    for irow, row in imt.iterrows():
        rn = row.name
        for k, v in row.items():
            if pd.isnull(v):
                continue
            rc += [(rn, k)]

    rc = list(zip(*rc))

    if len(rc) == 0:
        row_, col_ = [], []
    else:
        row_, col_ = rc[0], rc[1]

    return imt, pd.DataFrame(data={'row': row_, 'col': col_})
