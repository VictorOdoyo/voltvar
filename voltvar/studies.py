import hashlib,json
from .model import validate
from .evaluate import assess
from .control import local_control,optimize
from .profiles import time_series,uncertain_solar
def run(model,action='analyze',options=None):
    m=validate(model);options=options or {}
    if action=='analyze':result=assess(m,**options)
    elif action=='optimize':result=optimize(m,**options)
    elif action=='local':result=local_control(m,**options)
    elif action=='time_series':result=time_series(m,m['profile'],**options)
    elif action=='uncertainty':result=uncertain_solar(m,options.get('scales',[.5,.8,1]),q_levels=options.get('q_levels',3))
    else:raise ValueError('Unknown study')
    result['provenance']={'sha256':hashlib.sha256(json.dumps(model,sort_keys=True,allow_nan=False).encode()).hexdigest(),'action':action,'options':options,'version':'1.0.0'}
    return result
