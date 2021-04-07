'''
Disable a package so it is hidden from resolves.
'''
from __future__ import print_function


# TEMP COMMENT PLS REMOVE

def setup_parser(parser, completions=False):
    parser.add_argument(
        "-u", "--unignore", action="store_true",
        help="Unignore a package.")
    PKG_action = parser.add_argument(
        "PKG", type=str,
        help="The exact package to (un)ignore (eg 'foo-1.2.3').")
    parser.add_argument(
        "PATH", nargs='?',
        help="The repository containing the package. If not specified, this "
        "command will present you with a list to select from.")

    if completions:
        from rez.cli._complete_util import PackageCompleter
        PKG_action.completer = PackageCompleter


def list_repos_containing_pkg(pkg_name, pkg_version):
    from rez.config import config
    from rez.package_repository import package_repository_manager
    import sys

    # search for package in each searchpath
    matching_repos = []

    for path in config.packages_path:
        repo = package_repository_manager.get_repository(path)

        fam = repo.get_package_family(pkg_name)
        if fam is None:
            continue

        for pkg in fam.iter_packages():
            if pkg.version == pkg_version:
                matching_repos.append(repo)
                break

    if matching_repos:
        print("No action taken. Run again, and set PATH to one of:")
        for repo in matching_repos:
            print(str(repo))
    else:
        print("Package not found.", file=sys.stderr)
        sys.exit(1)


def command(opts, parser, extra_arg_groups=None):
    from rez.package_repository import package_repository_manager
    from rez.vendor.version.requirement import VersionedObject
    import sys

    obj = VersionedObject(opts.PKG)

    if opts.PATH is None:
        list_repos_containing_pkg(obj.name, obj.version)
        sys.exit(0)

    repo = package_repository_manager.get_repository(opts.PATH)

    if opts.unignore:
        i = repo.unignore_package(obj.name, obj.version)
    else:
        i = repo.ignore_package(obj.name, obj.version)

    if i == 1:
        if opts.unignore:
            print("Package is now visible to resolves once more")
        else:
            print("Package is now ignored and will not be visible to resolves")
    elif i == 0:
        if opts.unignore:
            print("No action taken - package was already visible")
        else:
            print("No action taken - package was already ignored")
    else:
        print("Package not found", file=sys.stderr)
        sys.exit(1)
