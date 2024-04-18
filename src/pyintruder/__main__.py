import argparse
from . import Basic
import importlib_resources
import logging
import pathlib
import typing
import asyncio
import sys

class ListDictsAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, default=None,type=None,choices=None,required=False,help=None,metavar=None):
        _option_strings = list(option_strings)
        super(ListDictsAction,self).__init__(option_strings=_option_strings,dest=dest,nargs=nargs,default=default,type=type,choices=choices,required=required,help=help,metavar=metavar)

    def __call__(self,parser,namespace,values,option_string=None):
        Tr = importlib_resources.files("pyintruder.dictionaries")
        for file in Tr.iterdir():
            with importlib_resources.as_file(file) as path:
                if path.is_file() and path.suffix == '.txt':
                    print(path.name)
        
        parser.exit()

parser = argparse.ArgumentParser(
    prog='pyintruder',
    description="Runs brute-force attacks on a website using python format strings replaced with elements from dictionaries",
    epilog="For more information visit https://github.com/Lukerd-29-00/pyintruder"
)
parser.add_argument(
    '-l',
    '--ls',
    metavar="list dictionaries",
    dest="ls",
    action=ListDictsAction,
    help="List the dictionaries available by default in the package."
)

parser.add_argument(
    'template_file',
    metavar="Template-file",
    action="store",
    help="The file containing the base request."
)
parser.add_argument(
    'host',
    metavar="host",
    action='store',
    help="The target of the attack."
)
parser.add_argument(
    '-v',
    '--verbose',
    metavar="verbose",
    action="store_const",
    const=True,
    default=False,
    required=False,
    help="Log debug messages to stdout"
)
parser.add_argument(
    '-s',
    '--no-ssl',
    metavar="disable SSL",
    action="store_const",
    const=False,
    default=True,
    required=False,
    help="Disable SSL certificate verification"
)

parser.add_argument(
    '-d',
    '--dictionaries',
    metavar="dictionaries",
    required=True,
    dest="dictionaries",
    action='append',
    type=str,
    help="A mapping of template variables to dictionary files in format variable,path.",
)

parser.add_argument(
    '-b',
    '--batch-size',
    metavar="batch size",
    required=False,
    type=int,
    action="store",
    dest="batch_size",
    default=10
)

def starts_with_pwd(path: str):
    return len(path) >= 2 and (path[:2] == './' or path[:2] == '.\\')

async def main(template_file: str, dictionaries: str, verbose: bool, host: str, batch_size: int):
    if verbose:
        logger = logging.getLogger("Intruder")
        sh = logging.StreamHandler(stream=sys.stderr)
        sh.setLevel(logging.DEBUG)
        logger.addHandler(sh)
        logger.setLevel(logging.DEBUG)
    
    template_file = pathlib.Path(template_file)
    if not template_file.exists():
        raise ValueError(f"template file {template_file} not found")
    if not template_file.is_file():
        raise ValueError(f"template must be a file: got {template_file}")
    vars_to_files = {}
    default_files = set()
    Tr = importlib_resources.files("pyintruder.dictionaries")

    for file in Tr.iterdir():
        with importlib_resources.as_file(file) as path:
            default_files.add(path.name)

    for arg in dictionaries:
        split_arg: typing.List[str] = arg.split(',')
        if len(split_arg) != 2:
            raise ValueError(f"dictionary {arg} is not a valid format; there should be exactly one ',' character.")
        var, file = tuple(split_arg)
        pth = pathlib.Path(file)
        if starts_with_pwd(file) or pth.is_absolute():
            if not pth.exists():
                raise ValueError(f"File not found: {file}")
            if not pth.is_file():
                raise ValueError(f"Not a valid file: {file}")
            vars_to_files[var] = pth
        elif len(pth.parts) == 1 and pth.name in default_files:
            target = Tr.joinpath(pth)
            with importlib_resources.as_file(target) as pth:
                vars_to_files[var] = pth
        else:
            if not pth.exists():
                raise ValueError(f"File not found: {file}")
            if not pth.is_file():
                raise ValueError(f"Not a valid file: {file}")
            vars_to_files[var] = pth

    with Basic.StatusCodePitchforkIntruderSession(host,template_file,vars_to_files) as intruder:
        data = await intruder.intrude(batch_size=batch_size)
    files = {}
    for k in vars_to_files.keys():
        files[k] = (vars_to_files[k].open())

    printme = ""
    for item in data:
        first = True
        for k in vars_to_files.keys():
            if first:
                printme += f"{k}={files[k].readline().strip()}"
                first = False
            else:
                printme += f", {k}={files[k].readline().strip()}"
        printme += f": {item}\n"
    print("-----RESULTS-----")
    print(printme,end='')
    print("-----------------")


if __name__ == "__main__":
    args = parser.parse_args()

    template_file = args.template_file
    dictionaries = args.dictionaries
    verbose = args.verbose
    host = args.host
    batch_size = args.batch_size

    asyncio.run(main(template_file,dictionaries,verbose,host,batch_size))