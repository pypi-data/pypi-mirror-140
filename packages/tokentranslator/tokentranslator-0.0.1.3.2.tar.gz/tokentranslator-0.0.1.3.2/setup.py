# must be outside tokentranslator
import os
import sys

from setuptools import setup, find_packages, find_namespace_packages

from setuptools.command.install import install
from setuptools.command.develop import develop

# from pkg_resources import get_distribution, DistributionNotFound

# import setuptools_scm
from setuptools_scm import get_version
# from setuptools_scm.integration import find_files

# tokentranslator
this_dir = os.path.dirname(os.path.realpath(__file__))


# FOR setup args:
class CommandMixin(object):
    '''
    For using arguments in pip for both install and development mode:

    pip install -v --install-option="--dialect=wolfram" dist/tokentranslator-0.0.1.2.dev8.tar.gz
    or
    pip install  -v --install-option="--dialect=wolfram" -e .

    # REF: https://stackoverflow.com/questions/18725137/how-to-obtain-arguments-passed-to-setup-py-from-pip-with-install-option#

    '''
    user_options = [
        ('someopt', None, 'a flag option'),
        ('dialect=', None, 'an option that takes a value')
    ]

    def initialize_options(self):
        super().initialize_options()
        # Initialize options
        self.someopt = None
        self.dialect = "tex"

    def finalize_options(self):
        # Validate options
        # if self.someval < 0:
        #     raise ValueError("Illegal someval!")
        # print("INFO: finalize dialect: ", self.dialect)
        # print("install_dir: ", self.install_dir)
        # print("installed_projects: ", self.installed_projects)

        super().finalize_options()

    def run(self):
        # Use options
        global dialect
        dialect = self.dialect  # will be 1 or None
        # print("INFO: run dialect:", dialect)
        # print("self.distribution")
        # print(dir(self.distribution))
        super().run()


class InstallCommand(CommandMixin, install):
    user_options = (getattr(install, 'user_options', [])
                    + CommandMixin.user_options)


class DevelopCommand(CommandMixin, develop):
    user_options = (getattr(develop, 'user_options', [])
                    + CommandMixin.user_options)
# END FOR


def change_db_path(installed_projects, install_lib):
    '''
    Change db entries in 'tokentranslator/configs/config_patterns_db.json'
    file as they given in 
    pip install -v --install-option="--dialect=wolfram" dist/tokentranslator-0.0.1.2.dev8.tar.gz
    or
    pip install  -v --install-option="--dialect=wolfram" -e .

    if first case either virtual environment or global site-packages will be used
    if second case local folder will be used (development mode)
    '''
    # where project to be installed:
    path_root = None

    if "tokentranslator" in installed_projects:
       
        print("INFO: installed_projects.module_path: ",
              installed_projects['tokentranslator'].module_path)
        print("INFO: installed_projects.location: ",
              installed_projects['tokentranslator'].location)

        # if develop mode then location will point at source folder:
        # from which pip install -e . is used
        path_root = installed_projects['tokentranslator'].location
        path_root = os.path.join(path_root, "tokentranslator")
    else:
        print("INFO: installed_projects failed")
    
    # if not develop mode then installed:
    if path_root is None:
        path_root = install_lib
        # path_root = installed.command_obj['install'].install_lib
        path_root = os.path.join(path_root, "tokentranslator")

    cmd = ["--dialect" in arg for arg in sys.argv]
    if True in cmd:
        dialect = sys.argv[cmd.index(True)].split("=")[1]
    else:
        dialect = "tex"
    print("INFO: dialect:", dialect)

    # path_root = os.path.dirname(tokentranslator.__file__)
    print("IFNO: path_root:", path_root)

    # to change to tex use commands:
    if dialect == "tex":
        path = os.path.join(
            path_root,
            "db_models/data/eqs/tex_dialect.db")
    elif dialect == "wolfram":
        path = os.path.join(
            path_root,
            "db_models/data/eqs/demo_dialect.db")
    else:
        raise(Exception("dialect must be either tex or wolfram"))

    # FOR change dialect path:
    # import tokentranslator
    from tokentranslator.db_models.model_main import TokenizerDB
    # from tokentranslator.gui.web.model.model_main import TokenizerDB
    model = TokenizerDB()
    
    # for pip install -e . first time
    try:
        '''
        # this not working here because root path
        # changed during installation and depend on 
        # dev mode also
        # sometimes it can install even in tmp folder
        if dialect == "tex":
            model.change_eqs_to_tex()
        elif dialect == "wolfram":
            model.change_eqs_to_wolfram()
        '''
        model.set_and_change_default_path_for_dialect("eqs", path)
    except:
        print("WARNING: pip install -e . first time run error")
    # END FOR


def installator():
    print("\nDEV: this_dir:")
    print(this_dir)
    print("\nDEV: find_packages:")
    lpackages = find_packages('.')
    print(lpackages)

    print("\nINFO: get_version:")
    try:
        # local_scheme for pypi:
        print(get_version(root='.', relative_to=__file__,
                          local_scheme="no-local-version"))
    except:
        
        raise(BaseException("setuptools_scm get_version bug,"
                            + " update to v 3.5.0 needed:"
                            + " pip uninstall setuptools_scm"
                            + "\n pip install -Iv setuptools_scm>=3.5.0"))
        
    # for description:
    with open("README.md") as f:
        long_description = f.read()
    
    # for requirements:
    with open("requirements.ini") as f:
        s_reguirements = f.read()
    requirements = s_reguirements.split("\n")
    print("\nINFO: requirements:")
    print(requirements)    

    installed = setup(
        cmdclass={
            'install': InstallCommand,
            'develop': DevelopCommand,
        },
        
        name="tokentranslator",

        # use version (only) from setuptools_scm:
        use_scm_version={
            "root": ".",
            "relative_to": __file__,
            "local_scheme": "no-local-version"
        },

        # use_scm_version=True,
        # version=get_version(root='.', relative_to=__file__),

        author="tokentranslator-group",
        author_email="",
        description="token translator framework",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/tokentranslator-group/tokentranslator",
        packages=lpackages,

        # only data from git will be included (use_scm_version):
        include_package_data=True,
        
        # exclude_package_data={"hybriddomain.tests":
        #                       ["*.json", "*.ipynb",
        #                        "problems/*", "settings/*"]},
        # for ``include_package_data`` to work accordingly to git:
        # setuptools_scm will register itself as setuptools plug in,
        # with use of ``entry_points``, so it's git/hg ``file_finders``
        # will be implicitly used for finding only git/hg managable files
        # (that not in .{git/hg}ignore) when ``include_package_data``
        # or ``package_data`` attributes of setuptools.setup() was used.
        # (see https://github.com/pypa/setuptools_scm/blob/master/setup.py)

        # this will automatically used due to setup_requires setuptools_scm
        # (it will add it's entry_points to the setuptools during install):
        # entry_points="""
        # [setuptools.file_finders]
        # setuptools_scm = setuptools_scm.integration:find_files
        # """,

        setup_requires=['setuptools_scm >= 3.5.0'],
        # setup_requires=[ "setuptools_git >= 0.3", ],
        install_requires=requirements
    )

    # print("installed:")
    # print(dir(installed))
    print("DEV: get_command_obj('install')")
    inst = installed.get_command_obj('install')
    inst.ensure_finalized()
    # inst.run()

    print("DEV: get_command_obj('develop')")
    dev = installed.get_command_obj('develop')

    # if not do that, it crash during installation
    try:
        dev.ensure_finalized()
    except Exception as e:
        print(e)
        print("WARNING: dev.ensure_finalized faild. Probably in install mode.")
    # dev.run()

    print("DEV: command_obj[develop].install_dir:")
    print(installed.command_obj['develop'].install_dir)

    installed_projects = installed.command_obj['develop'].installed_projects
    print("DEV: command_obj[develop].installed_projects:")
    print(installed_projects)

    install_lib = installed.command_obj['install'].install_lib
    print("DEV: install_lib: ", install_lib)
    
    change_db_path(installed_projects, install_lib)


if __name__ == "__main__":
    installator()
