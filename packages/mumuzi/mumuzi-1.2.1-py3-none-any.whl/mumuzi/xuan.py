 # -*- coding: utf-8 -*-

from .riposte import Riposte
from .riposte.printer import Palette
from .xuan_func import *
from colorama import init
init(autoreset=True)

class Application:
    def __init__(self):
        self.module = "~"


class CustomRiposte(Riposte):
    @property
    def prompt(self):
        if app.module:
            return f"\033[0;32mXuan:{app.module} > \033[0m"
        else:
            return self._prompt  # reference to `prompt` parameter.

app = Application()
XUAN = CustomRiposte(banner=get_banner(),prompt="\033[0;32mXuan:~ > \033[0m")
Exploit_Details={}

@XUAN.command("help")
def xuan_help(command=None):
    XUAN.print(command_help(command))

@XUAN.command("exit")
def xuan_exit():
    XUAN.print("bye!")
    exit()

@XUAN.command("set")
def xuan_set(msg):
    if msg.count('=')==1:
        Exploit_Details[msg.split('=')[0]]=msg.split('=')[1]
        XUAN.success(msg)
    else:
        XUAN.error('set error!')

@XUAN.command("info")
def xuan_info(module_path=None):
    if module_path is None:
        if app.module=="~":
            XUAN.error('no module name!!')
            return
        else:
            module_path=app.module
    success,msg=get_module_info(module_path,Exploit_Details)
    if success:
        XUAN.print(msg)
    else:
        XUAN.error(msg)

@XUAN.command("options")
def xuan_options(module_path=None):
    if module_path is None:
        if app.module=="~":
            XUAN.error('no module name!!')
            return
        else:
            module_path=app.module
    success,msg=get_module_info(module_path,Exploit_Details)
    if success:
        XUAN.print("\nModule options:"+msg.split("Module options:")[-1])
    else:
        XUAN.error(msg)

@XUAN.command("use")
def xuan_use(module_path):
    success,result=get_module_fullpath_and_infodata(module_path)
    if success:
        app.module=result[0]
        XUAN.success('Module has been set.')
    else:
        XUAN.error('Module name error!')

@XUAN.command("run")
@XUAN.command("exploit")
def xuan_run(module_path=None):
    if module_path is None:
        if app.module=="~":
            XUAN.error('no module name!!')
            return
        else:
            module_path=app.module
    XUAN.success('running exploit......')
    success,msg=run_module(module_path,Exploit_Details)
    if success:
        XUAN.success("exploit completed.....")
        XUAN.success(msg)
    else:
        XUAN.error(msg)
    
@XUAN.command("search")
def xuan_search(querystring: str):
    success,msg=search_from_all_modules(querystring)
    if success:
        XUAN.print(msg)
    else:
        XUAN.error(msg)

@XUAN.command("show")
def xuan_show(module_type=None):
    success,msg=show_all_modules(module_type)
    if success:
        XUAN.print(msg)
    else:
        XUAN.error(msg)

@XUAN.command("tao")
def xuan_tao(module_path=None):
    if module_path is None:
        if app.module=="~":
            XUAN.error('no module name!!')
            return
        else:
            module_path=app.module
    XUAN.success('making writeup......')
    success,msg=make_wp(module_path)
    if success:
        with open('wp.md','wb')as f:
            f.write(msg.encode('utf-8'))
        XUAN.success("your writeup is in wp.md")
    else:
        XUAN.error(msg)

XUAN.run()




