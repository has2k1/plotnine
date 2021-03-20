import sys
import argparse

import plotnine as p9
import pandas as pd
from datetime import date

def parse_kwargs(kwargs):
    def parse_val(v):
        try:
            return int(v)
        except Exception as e:
            try:
                return float(v)
            except Exception as e:
                return v

    return { k: parse_val(v) for k,v in [a.split('=', 1) for a in kwargs] }

def parse_scale_kwargs(kwargs):
    kwargs = parse_kwargs(kwargs)
    if 'min' in kwargs or 'max' in kwargs:
        kwargs['limits'] = ( kwargs.pop('min', None), kwargs.pop('max', None) )
    return kwargs

def get_geom(geom):
    return getattr(p9, f'geom_{geom}')

def get_stat(stat):
    return getattr(p9, f'stat_{stat}')

def get_scale(scale):
    (p1, p2) = scale.split('=', 1)
    name = f'scale_{p1}_{p2}'
    return getattr(p9, name)

def get_facet(facet):
    return getattr(p9, f'facet_{facet}')

def parse_command_line(argv):
    parser = argparse.ArgumentParser()
    dataset_group = parser.add_mutually_exclusive_group()
    dataset_group.add_argument('--dataset')
    dataset_group.add_argument('--input', '-i')
    parser.add_argument('--geom', '-g', action='append', nargs='+')
    parser.add_argument('--stat', '-s', action='append', nargs='+')
    parser.add_argument('--scale', action='append', nargs='+')
    parser.add_argument('--facet', '-f', nargs='+')
    parser.add_argument('--xlab')
    parser.add_argument('--ylab')
    parser.add_argument('--title')
    parser.add_argument('aes', nargs='*')

    args = parser.parse_args(argv)

    if args.dataset is None and args.input is None:
        args.input = '-'

    args.aes = p9.aes(**parse_kwargs(args.aes))
    args.geom = [ get_geom(g[0])(**parse_kwargs(g[1:]))
                  for g in args.geom or [] ]
    args.stat = [ get_stat(s[0])(**parse_kwargs(s[1:]))
                  for s in args.stat or [] ]
    args.scale = [ get_scale(s[0])(**parse_scale_kwargs(s[1:]))
                   for s in args.scale or [] ]
    if args.facet:
        args.facet = get_facet(args.facet[0])(**parse_kwargs(args.facet[1:]))

    return args

def main():
    args = parse_command_line(sys.argv[1:])

    if args.input:
        file = args.input if args.input != '-' else sys.stdin
        data = pd.read_csv(file, sep=None, engine='python')
    else:
        import plotnine.data
        data = getattr(plotnine.data, args.dataset)

    geoms = args.geom or None
    stats = args.stat or None
    scales = args.scale or None
    facet = [args.facet] if args.facet is not None else None
    title = p9.ggtitle(args.title) if args.title is not None else None
    xlab = p9.xlab(args.xlab) if args.xlab is not None else None
    ylab = p9.ylab(args.ylab) if args.ylab is not None else None

    default_geom = \
        [p9.geom_point()] if geoms is None and stats is None else None

    parts = []
    for x in [default_geom, geoms, stats, scales, facet, title, xlab, ylab]:
        if x is not None:
            parts.extend(x)

    (p9.ggplot(data, args.aes) + parts).draw(show=True)

if __name__ == '__main__':
    main()
