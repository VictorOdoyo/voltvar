import argparse,json
from pathlib import Path
from importlib.resources import files
from .studies import run
def example_names():return sorted(p.name[:-5] for p in files('voltvar').joinpath('examples').iterdir() if p.name.endswith('.json'))
def load_case(path):
    if path.startswith('example:'):
        name=path.split(':',1)[1]
        if name not in example_names():raise ValueError('Unknown example')
        return json.loads(files('voltvar').joinpath('examples',name+'.json').read_text(encoding='utf-8'))
    return json.loads(Path(path).read_text(encoding='utf-8'))
def main():
    parser=argparse.ArgumentParser(description='VoltVAR engineering studies');sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('examples');s=sub.add_parser('serve');s.add_argument('--port',type=int,default=8772)
    s=sub.add_parser('study');s.add_argument('path');s.add_argument('--action',choices=['analyze', 'optimize', 'local', 'time_series', 'uncertainty'],default='analyze');s.add_argument('--options',default='{}');s.add_argument('--output')
    args=parser.parse_args()
    try:
        if args.command=='examples':print('\n'.join(example_names()))
        elif args.command=='serve':
            from .server import serve
            serve(args.port)
        else:
            text=json.dumps(run(load_case(args.path),args.action,json.loads(args.options)),indent=2,allow_nan=False)
            if args.output:Path(args.output).write_text(text,encoding='utf-8')
            else:print(text)
    except (ValueError,KeyError,TypeError,ArithmeticError,OSError) as exc:parser.exit(2,str(exc)+'\n')
if __name__=='__main__':main()
