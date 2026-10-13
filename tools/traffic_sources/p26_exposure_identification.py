"""RITHM-2.7 P26 exact LATENT-attention measurement equivalence.

2017 experimental C-stage source rates, not observed advice readership or
new trial compliance. The math is ordinary 2-component Bernoulli mixture.
"""
import json

CB_NORMAL=869/1399
CB_INCIDENT=7/370

def worlds(normal=CB_NORMAL,incident=CB_INCIDENT):
    assert 0<=incident<=normal<=1
    diff=normal-incident
    all_read=dict(attention=1, nonreader=0, reader_normal=normal, reader_incident=incident)
    alpha=(1+diff)/2
    partial=dict(attention=alpha, nonreader=incident/(1-alpha),
                 reader_normal=diff/alpha,reader_incident=0)
    for world in [all_read,partial]:
        a=world['attention'];b=world['nonreader']
        assert abs(normal-((1-a)*b+a*world['reader_normal']))<1e-12
        assert abs(incident-((1-a)*b+a*world['reader_incident']))<1e-12
        assert all(0<=v<=1 for v in world.values())
    return {'conditional_CB_given_actual_C_entry_info_arm':
               {'normal':normal,'incident':incident,'n_normal':1399,'n_incident':370},
            'all_read_compatible':all_read,'partial_read_compatible':partial,
            'hypothetical_nonreader_invariant_bounds':{'min':diff,'max':1},
            'CAUTION':'Zero actual per-person read/render/view log. Toy bound valid only with unverified constant fraction, state-invariant nonreaders and comparable C-entry selection. No empirically observed attention percentage or causal policy effect.'}

if __name__=='__main__':
    print(json.dumps(worlds(),indent=2))
