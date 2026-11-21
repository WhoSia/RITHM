"""Run the source-sealed R58 LOSO with public-safe aggregate output only."""
import argparse,json
from pathlib import Path
from r58_matched_cv import aggregate
from r58_provenance import assert_result_cohort


def run(source,*,lapse=.02,bootstrap=2000):
    result=aggregate(source,lapse=lapse,bootstrap=bootstrap)
    assert_result_cohort(result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('author_approved_zip',type=Path)
    p.add_argument('--lapse',type=float,default=.02)
    p.add_argument('--bootstrap',type=int,default=2000)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    result=run(a.author_approved_zip,lapse=a.lapse,bootstrap=a.bootstrap)
    content=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n'
    if a.output:
        a.output.write_text(content,encoding='utf-8')
        print('Wrote aggregate-only R58 results:',a.output)
    else:print(content,end='')
