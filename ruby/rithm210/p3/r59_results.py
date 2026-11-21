"""Aggregate-only R59 source/rollout verdict; no session or person rows.

Rebuilds the public report from independently sealed source-level aggregate
simulation outputs. This does NOT ingest untrusted arbitrary participant rows.
"""
from pathlib import Path
from math import sqrt
import json

SOURCE='e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
EXPECTED=(('r59_observed_primary.json','observed','tape',.02),
          ('r59_fair_primary.json','fair','tape',.02),
          ('r59_observed_seed2_32.json','observed','tape',.02),
          ('r59_fair_seed2_32.json','fair','tape',.02),
          ('r59_fair_fresh.json','fair','fresh_uniform',.02),
          ('r59_fair_raw_ssm.json','fair','tape',0))


def root_on_nonnegative_axis(alt,base):
    a,b,c=(alt[k]-base[k] for k in ('A','B','D'))
    if c==0:
        if b==0:return None
        k=-a/b
        return k if k>=0 else None
    disc=b*b-4*c*a
    if disc<0:return None
    ks=sorted({(-b-sqrt(disc))/(2*c),(-b+sqrt(disc))/(2*c)})
    return next((k for k in ks if k>=0),None)


def summarize(directory):
    d=Path(directory)
    scenarios={}
    for name,init,shocks,lapse in EXPECTED:
        data=json.loads((d/name).read_text(encoding='utf-8'))
        if (data['source_sha256']!=SOURCE or data['sessions']!=24 or
            data['groups']!=144 or data['init']!=init or
            data['shocks']!=shocks or data['lapse']!=lapse or
            data['repetitions_per_group']!=32):
            raise ValueError('unsealed or mismatched scenario contract '+name)
        if {str(i) for i in (1,2,3)}!=set(data['observed']):
            raise ValueError('lost treatment code')
        h=(data.get('treatment_contrasts',{}).get('full_minus_no',{})
           .get('observed_arm_contrast'))
        if h is None:
            h={k:data['observed']['3'][k]-data['observed']['1'][k]
               for k in ('total_excess','total_gross','early_excess','late_excess')}
        scenario={'initial_routes':init,'exogenous_values':shocks,'ssm_lapse':lapse,
                  'repetitions_per_group':32,'models':{},
                  'historical_full_minus_no':h}
        for m,v in data['models'].items():
            o=v['overall']
            scenario['models'][m]={
                'predicted_total_excess_per_group':o['predicted_mean_per_group']['total_excess'],
                'predicted_total_gross_per_group':o['predicted_mean_per_group']['total_gross'],
                'mc_se_total_excess_mean':o['mc_se_over_groups']['total_excess'],
                'group_excess_total_MSE':o['mean_group_total_mse']['total_excess'],
                'group_total_gross_MSE':o['mean_group_total_mse']['total_gross'],
                'group_resource_prediction_mse_polynomial':o['joint_cost_mse_polynomial'],
                'by_treatment':{t:{
                    'excess':vv['predicted_mean_per_group']['total_excess'],
                    'gross':vv['predicted_mean_per_group']['total_gross'],
                    'early_excess':vv['predicted_mean_per_group']['early_excess'],
                    'late_excess':vv['predicted_mean_per_group']['late_excess'],
                    } for t,vv in v['by_treatment'].items()},
                'full_minus_no_excess_prediction':(
                    v['by_treatment']['3']['predicted_mean_per_group']['total_excess']-
                    v['by_treatment']['1']['predicted_mean_per_group']['total_excess']),
                'full_minus_no_excess_error_session_resampling':(
                    data.get('treatment_contrasts',{}).get('full_minus_no',{})
                    .get('models',{}).get(m,{}).get('contrast_error',{})
                    .get('total_excess')),
                }
        if 'private_history' in scenario['models'] and 'ssm1_9' in scenario['models']:
            pair=data.get('paired_session_resampling',{}).get('ssm1_9--private_history')
            if pair is not None:
                scenario['ssm1_9_minus_private_history_excess_mse_session_resampling']=pair['total_excess']
                scenario['ssm1_9_minus_private_history_kappa1_mse_session_resampling']=pair['resource_kappa1']
            scenario['resource_mse_nonnegative_switch_price_crossover_kappa']=root_on_nonnegative_axis(
                scenario['models']['ssm1_9']['group_resource_prediction_mse_polynomial'],
                scenario['models']['private_history']['group_resource_prediction_mse_polynomial'])
        scenarios[name.replace('r59_','').replace('.json','')]=scenario
    ref=json.loads((d/'r59_fair_primary.json').read_text(encoding='utf-8'))['observed']
    obs={t:{'per_group_excess':z['total_excess'],
            'per_group_gross':z['total_gross'],
            'early_excess':z['early_excess'],'late_excess':z['late_excess']}
         for t,z in ref.items()}
    prior=json.loads((d/'r59_prior_exposure_results.json').read_text(encoding='utf-8'))
    parity=json.loads((d/'r59_original_source_parity.json').read_text(encoding='utf-8'))
    if (prior['source_sha256']!=SOURCE or parity['source_sha256']!=SOURCE or
        prior['linked_actor_section_transitions']!=576 or
        parity['un_enriched_extra_20_period_pilot_rows']!=360 or
        parity['un_enriched_actor_gross_switches']!=8909):
        raise ValueError('source cross-file audit results failed')
    return {
        'source_sha256':SOURCE,
        'cohort':{'sessions':24,'group_sections':144,'periods':40,
                  'group_period_transitions':5616,
                  'individual_one_step_targets':33696,
                  'historical_excess_per_group_by_treatment':obs},
        'study_type':'retrospective closed-loop synthetic simulations and proof; not human causal effect',
        'filtration':'simultaneous six-person routes before any same-period congestion or Value is revealed; only self-generated histories and prior private information used',
        'simulation_seed_method':'source-session position and group position, no participant or session ID in output',
        'scenarios':scenarios,
        'previous_section_actor_reuse':prior,
        'independent_author_table_parity':parity,
        'interpretation':(
          'One-step observation-conditional predictive loss does not determine '+
          'autonomous rollout macro calibration; initialization, treatment '+
          'strata, exogenous Value tape, SSM lapse and external resource switch '+
          'price change predictive rankings. Source conditions and 24-session '+
          'resampling are descriptive; no mechanism or policy effect identified.'),
    }


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('aggregate_directory',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=summarize(a.aggregate_directory)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('Wrote',a.output,'with six source-sealed scenarios, no individuals')
