__version__ = "1.0"

import enum
import textwrap
from pprint import pprint


@enum.unique
class CommandType(enum.Enum):
    Branch = "Branch"
    Commit = "Commit"
    Conflict = "Conflict"
    Fetch = "Fetch"
    Index = "Index"
    Log = "Log"
    Merge = "Merge"
    Push = "Push"
    Remote = "Remote"
    Stash = "Stash"
    Tag = "Tag"
    WorkingTree = "Working tree"
    Submodule = "Submodule"
    Setting = "Setting"
    Extra = "Extra"  # default


# The custom git output format string.
#   git ... --pretty={0}.format(GIT_PRINT_FORMAT)
GIT_PRINT_FORMAT = (
    'format:"%C(bold yellow)commit %H%C(auto)%d%n'
    "%C(bold)Author: %C(blue)%an <%ae> %C(reset)%C(cyan)%ai (%ar)%n"
    '%C(bold)Commit: %C(blue)%cn <%ce> %C(reset)%C(cyan)%ci (%cr)%C(reset)%n%+B"'
)


Git_Cmds = {
    # Branch
    "b": {
        "belong": CommandType.Branch,
        "command": "git branch",
        "help": "lists, creates, renames, and deletes branches.",
        "type": "command",
        "has_arguments": True,
    },
    "bc": {
        "belong": CommandType.Branch,
        "command": "git checkout -b",
        "help": "creates a new branch.",
        "has_arguments": True,
    },
    "bl": {
        "belong": CommandType.Branch,
        "command": "git branch -vv",
        "help": "lists branches and their commits.",
    },
    "bL": {
        "belong": CommandType.Branch,
        "command": "git branch --all -vv",
        "help": "lists local and remote branches and their commits.",
    },
    "bs": {
        "belong": CommandType.Branch,
        "command": "git show-branch",
        "help": "lists branches and their commits with ancestry graphs.",
    },
    "bS": {
        "belong": CommandType.Branch,
        "command": "git show-branch --all",
        "help": "lists local and remote branches and their commits with "
        "ancestry graphs.",
    },
    "bm": {
        "belong": CommandType.Branch,
        "command": "git branch --move",
        "help": "renames a branch.",
        "has_arguments": True,
    },
    "bM": {
        "belong": CommandType.Branch,
        "command": "git branch --move --force",
        "help": "renames a branch even if the new branch name already exists.",
        "has_arguments": True,
    },
    "bd": {
        "belong": CommandType.Branch,
        "command": "git branch -d",
        "help": "delete a local branch by name.",
        "has_arguments": True,
    },
    # Commit
    "c": {
        "belong": CommandType.Commit,
        "command": "git commit --verbose",
        "help": "records changes to the repository.",
    },
    "ca": {
        "belong": CommandType.Commit,
        "command": "git commit --verbose --all",
        "help": "commits all modified and deleted files.",
    },
    "cA": {
        "belong": CommandType.Commit,
        "command": "git commit --verbose --patch",
        "help": "commits all modified and deleted files interactively",
    },
    "cm": {
        "belong": CommandType.Commit,
        "command": "git commit --verbose --message",
        "help": "commits with the given message.",
    },
    "co": {
        "belong": CommandType.Commit,
        "command": "git checkout",
        "help": "checks out a branch or paths to the working tree.",
        "has_arguments": True,
    },
}

repo_options = {
    "fetch": {"cmd": "git fetch", "allow_all": True, "help": "fetch remote update"},
    "pull": {"cmd": "git pull", "allow_all": True, "help": "pull remote updates"},
    "push": {"cmd": "git push", "allow_all": True, "help": "push the local updates"},
}


def _cmd_func(*args, **kwargs):
    pass


def _repo_func(*args, **kwargs):
    pass


argparse_dict = {
    "prog": "pigit",
    "prefix_chars": "-",
    "description": "Pigit TUI is called automatically if no parameters are followed.",
    "args": {
        "-v --version": {
            "action": "version",
            "help": "Show version and exit.",
            "version": f"Version: {__version__}",
        },
        "-r --report": {
            "action": "store_true",
            "help": "Report the pigit desc and exit.",
        },
        "-f --config": {
            "action": "store_true",
            "help": "Display the config of current git repository and exit.",
        },
        "-i --information": {
            "action": "store_true",
            "help": "Show some information about the current git repository.",
        },
        "-d --debug": {
            "action": "store_true",
            "help": "Current runtime in debug mode.",
        },
        "--out-log": {"action": "store_true", "help": "Print log to console."},
        "-groups": {
            "tools": {
                "title": "tools arguments",
                "description": "Auxiliary type commands.",
                "args": {
                    "-c --count": {
                        "nargs": "?",
                        "const": ".",
                        "type": str,
                        "metavar": "PATH",
                        "help": "Count the number of codes and output them in tabular form."
                        "A given path can be accepted, and the default is the current directory.",
                    },
                    "-C --complete": {
                        "action": "store_true",
                        "help": "Add shell prompt script and exit.(Supported bash, zsh, fish)",
                    },
                    "--create-ignore": {
                        "type": str,
                        "metavar": "TYPE",
                        "dest": "ignore_type",
                        "help": "Create a demo .gitignore file. Need one argument, support: [%s]",
                    },
                    "--create-config": {
                        "action": "store_true",
                        "help": "Create a pre-configured file of PIGIT."
                        "(If a profile exists, the values available in it are used)",
                    },
                },
            }
        },
        "cmd": {
            "help": "git short command.",
            "description": "If you want to use some original git commands, please use -- to indicate.",
            "args": {
                "command": {
                    "nargs": "?",
                    "type": str,
                    "default": None,
                    "help": "Short git command or other.",
                },
                "args": {"nargs": "*", "type": str, "help": "Command parameter list."},
                "-s --show-commands": {
                    "action": "store_true",
                    "help": "List all available short command and wealth and exit.",
                },
                "-p --show-part-command": {
                    "type": str,
                    "metavar": "TYPE",
                    "dest": "command_type",
                    "help": "According to given type [%s] list available short command and wealth and exit.",
                },
                "-t --types": {
                    "action": "store_true",
                    "help": "List all command types and exit.",
                },
                "--shell": {
                    "action": "store_true",
                    "help": "Go to the pigit shell mode.",
                },
                "set_defaults": {"func": _cmd_func},
                **{k: {"help": v["help"], "args": {}} for k, v in Git_Cmds.items()},
            },
        },
        "repo": {
            "help": "repo options.",
            "args": {
                "add": {
                    "help": "add repo(s).",
                    "args": {
                        "paths": {"nargs": "+", "help": "path of reps(s)."},
                        "--dry-run": {"action": "store_true", "help": "dry run."},
                        "set_defaults": {
                            "func": _repo_func,
                            "kwargs": {"option": "add"},
                        },
                    },
                },
                "rm": {
                    "help": "remove repo(s).",
                    "args": {
                        "repos": {"nargs": "+", "help": "name or path of repo(s)."},
                        "--path": {
                            "action": "store_true",
                            "help": "remove follow path, defult is name.",
                        },
                        "set_defaults": {
                            "func": _repo_func,
                            "kwargs": {"option": "rm"},
                        },
                    },
                },
                "rename": {
                    "help": "rename a repo.",
                    "args": {
                        "repo": {"help": "the name of repo."},
                        "new_name": {"help": "the new name of repo."},
                        "set_defaults": {
                            "func": _repo_func,
                            "kwargs": {"option": "rename"},
                        },
                    },
                },
                "ll": {
                    "help": "display summary of all repos.",
                    "args": {
                        "--simple": {
                            "action": "store_true",
                            "help": "display simple summary.",
                        },
                        "set_defaults": {
                            "func": _repo_func,
                            "kwargs": {"option": "ll"},
                        },
                    },
                },
                "clear": {
                    "help": "clear the all repos.",
                    "args": {
                        "set_defaults": {
                            "func": _repo_func,
                            "kwargs": {"option": "clear"},
                        },
                    },
                },
                **{
                    name: {
                        "help": prop["help"] + " for repo(s).",
                        "args": {
                            "repos": {"nargs": "*", "help": "name of repo(s)."},
                            "set_defaults": {
                                "func": _repo_func,
                                "kwargs": {"option": name},
                            },
                        },
                    }
                    for name, prop in repo_options.items()
                },
            },
        },
    },
}

_TEMPLATE: str = textwrap.dedent(
    """\
    #compdef %(prog)s

    #--------------------------------------------------------------------
    # This completion script is generated automatically by parsing
    # parameters.
    #
    #--------------------------------------------------------------------
    # Author
    #--------
    #
    # * Zachary Zhang (https://github.com/zlj-zz)
    #
    #--------------------------------------------------------------------

    %(tools)s

    complete_%(prog)s(){
      local curcontext="$curcontext" state line ret=1
      typeset -A opt_args

      %(arguments)s
      %(cases)s

      return ret
    }

    compdef complete_%(prog)s %(prog)s
    """
)

_TEMP_A = """
_arguments -C \\
%s
&& ret=0

"""

__TEMP_V = """\
__%s_values() {
  _values '' \\
%s
  && ret=0
}
"""


def _parse(args: dict):
    _arguments = []
    _positions = []
    _sub_opts = {}

    for name, prop in args.items():
        if name == "-groups":
            for g_name, g_p in prop.items():
                a, p, s = _parse(g_p["args"])
                _arguments.extend(a)
                _positions.extend(p)
        elif name == "set_defaults":
            # Special need be ignore.
            pass
        elif "args" in prop:
            a, p, s = _parse(prop["args"])
            _sub_opts[name] = {
                "_arguments": a,
                "_pisitions": p,
                "_sub_commands": s,
                "cmd_str": f"'{name}[{prop['help']}]' \\",
            }
        elif name.startswith("-"):
            names = name.split()
            if len(names) == 1:
                _arguments.append(f"'{name}[{prop['help']}]' \\")
            else:
                _arguments.append(
                    "{%(keys)s}'[%(desc)s]' \\"
                    % {"keys": ",".join(names), "desc": prop["help"]}
                )
        else:
            _positions.append(f"'{name}[{prop['help']}]' \\")

    return _arguments, _positions, _sub_opts


def _process_sub_commands(
    _sub_opts: dict, _sub_opt_comps: list, relationship: list, idx: int = 1
):
    relation_str = ""

    for name, d in _sub_opts.items():

        _a = d.get("_arguments", [])
        _s = []
        if _sub_c := d.get("_sub_commands"):
            for x in _sub_c.values():
                if cmd_str := x.get("cmd_str"):
                    _s.append(cmd_str)
            _process_sub_commands(_sub_c, _sub_opt_comps, relationship, idx + 1)
        if _a or _s:
            _sub_opt_comps.append(
                __TEMP_V % (name, textwrap.indent("\n".join([*_a, *_s]), "    "))
            )
            relation_str += f"    {name}) __{name}_values ;;\n"

    if relation_str:
        relation_str = (
            textwrap.dedent(
                """
                if [[ ${#line} -eq %s ]]; then
                  case $line[%s] in
                %s
                  esac
                fi
                """
            )
            % (idx + 1, idx, relation_str)
        )
        relationship.append(relation_str)


def args2complete(d):
    prog_handle: str = d["prog"]
    args: dict = d["args"]

    _arguments, _positions, _sub_opts = _parse(args)

    _sub_opt_str = ""
    _sub_opt_comps = []
    _sub_relationship = []

    if _sub_opts:
        _subs = []
        for x in _sub_opts.values():
            _subs.append(x["cmd_str"])
        _sub_opt_str = textwrap.dedent(
            """
            ######################
            # sub-commands helper
            ######################
            """
        ) + __TEMP_V % (
            "sub_opt",
            textwrap.indent("\n".join(_subs), "    "),
        )

        _process_sub_commands(_sub_opts, _sub_opt_comps, _sub_relationship, idx=1)

    _opt_case_str = ""

    if _sub_opt_str:
        _arguments.append("'1: :->opts'\\")
        _opt_case_str = textwrap.dedent(
            """
            case $state in
              opts) __sub_opt_values ;;
            """
        )

    if _sub_opt_comps:
        _arguments.append("'*::arg:->args'\\")
        _opt_case_str += "  args)\n"
        _opt_case_str += textwrap.indent("\n".join(_sub_relationship), " " * 4)

    if _opt_case_str:
        _opt_case_str += "esac"

    arguments_str = _TEMP_A % textwrap.indent("\n".join(_arguments), " " * 2)

    return _TEMPLATE % {
        "prog": prog_handle,
        "tools": "\n".join([*_sub_opt_comps, _sub_opt_str]),
        "arguments": textwrap.indent(arguments_str, " " * 2),
        "cases": textwrap.indent(_opt_case_str, " " * 2),
    }


"""
    case $state in
        cmds)
            __sub_commands
            ;;
        args)
            case $line[1] in
                cmd)
                    _values 'cmd options'\
                        "b[lists, creates, renames, and deletes branches.]"\
                        "bc[creates a new branch.]"\
                        "bl[lists branches and their commits.]"\
                        "bL[lists local and remote branches and their commits.]"\
                        "bs[lists branches and their commits with ancestry graphs.]"\
                        "bS[lists local and remote branches and their commits with ancestry graphs.]"\
                        "bm[renames a branch.]"\
                        "bM[renames a branch even if the new branch name already exists.]"\
                        "bd[delete a local branch by name.]"\
                    && ret=0
                    ;;
                repo)
                    _values 'repo options'\
                        'add[add repo(s).]'\
                        'rm[remove repo(s).]'\
                        'rename[rename a repo.]'\
                    && ret=0

            esac
    esac

"""
if __name__ == "__main__":

    print(args2complete(argparse_dict))
