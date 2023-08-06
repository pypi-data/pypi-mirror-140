from setuptools import setup, Extension

setup(
    name="XpongeLib",
    version="0.0.8.8.1",
    author="Yijie Xia",  
    author_email="yijiexia@pku.edu.cn", 
    description="the C++ Lib for the package for building molecular dynamics inputs for SPONGE",
    url="https://gitee.com/gao_hyp_xyj_admin/xponge",
    #data_files = [("parmchk_mod", ["parmchk_mod/gaff.dat", "parmchk_mod/gaff2.dat", "parmchk_mod/PARMCHK.DAT", "parmchk_mod/PARM_BLBA_GAFF.DAT", "parmchk_mod/PARM_BLBA_GAFF2.DAT", "parmchk_mod/CONNECT.TPL"])],
    package_data = {"XpongeLib.parmchk_mod":
          ["parmchk_mod/*.dat", "parmchk_mod/*.DAT", "parmchk_mod/CONNECT.TPL"]},
    ext_modules = [Extension("XpongeLib", ["main.c"])]
)
