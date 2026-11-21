"""R60 operator: local approved ZIP -> only whole-cohort aggregate JSON files.

Never print or write raw human actor / session / group rows.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json
from r59_prior_exposure import parse_source_section_histories
from r60_cross_segment import run,events_from_histories
from r60_identity_placebo import build_cost_matrices,permutation_check
from r60_latent_rival import exact_nonidentification
from r54_original_batch_clock import APPROVED_ZIP_SHA256


def generate(original,output):
    raw=Path(original).read_bytes()
    if sha256(raw).hexdigest()!=APPROVED_ZIP_SHA256:
        raise ValueError('refuse any original human ZIP not matching approved SHA-256')
    path=Path(output)
    if not path.is_dir():raise ValueError('must supply pre-existing output directory')
    aggregate=run(original)
    people=parse_source_section_histories(original)
    events,_=events_from_histories(people)
    placebo=permutation_check(build_cost_matrices(events),reps=2000,seed=20261121)
    placebo['exact_rival']=exact_nonidentification()
    for name,result in [('r60_results.json',aggregate),('r60_identity_placebo.json',placebo)]:
        (path/name).write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return {name:sha256((path/name).read_bytes()).hexdigest()
            for name in ('r60_results.json','r60_identity_placebo.json')}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('approved_original_zip')
    parser.add_argument('existing_output_directory')
    args=parser.parse_args()
    print(json.dumps(generate(args.approved_original_zip,args.existing_output_directory),indent=2))
