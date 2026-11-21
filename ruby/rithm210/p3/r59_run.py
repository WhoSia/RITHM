"""Operator-only entrypoint to rerun R59 from the authorized private ZIP.

Only whole-cohort aggregate JSON is written, never private session/group/actor
ids, route rows or individual exogenous Value. This program has no network.
"""
import argparse
import json
from pathlib import Path
from r59_closed_loop import MODELS,run_experiment


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('approved_source_zip',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--initial-routes',choices=('observed','fair'),default='fair')
    parser.add_argument('--exogenous-values',choices=('tape','fresh_uniform'),default='tape')
    parser.add_argument('--repetitions',type=int,default=32)
    parser.add_argument('--seed',type=int,default=20261121)
    parser.add_argument('--ssm-lapse',type=float,default=.02)
    parser.add_argument('--ssm-only',action='store_true')
    args=parser.parse_args()
    if args.output.resolve()==args.approved_source_zip.resolve():
        parser.error('output must not overwrite the restricted source ZIP')
    res=run_experiment(args.approved_source_zip,repetitions=args.repetitions,
        seed=args.seed,init=args.initial_routes,shocks=args.exogenous_values,
        lapse=args.ssm_lapse,
        models=(('ssm5','ssm1_9') if args.ssm_only else MODELS))
    args.output.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('R59 aggregate-only output:',str(args.output),'sessions',res['sessions'],
          'group sections',res['groups'])


if __name__=='__main__':main()
