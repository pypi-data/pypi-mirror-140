import ctypes
import os
from subprocess import Popen, PIPE

from comtypes.client import CreateObject


class RegDm:

    @classmethod
    def reg(cls):
        path = os.path.dirname(__file__)
        reg_dm = ctypes.windll.LoadLibrary(path + r'\DmReg.dll')
        reg_dm.SetDllPathW(path + r'\dm.dll', 0)
        return CreateObject(r'dm.dmsoft')

    @classmethod
    def CreateDm(cls):
        return CreateObject(r'dm.dmsoft')


class 雷电命令:
    def __init__(self, path: str):
        os.putenv('Path', path)

    def 读取命令信息(self, cmd):
        res = Popen(cmd, stdout=PIPE, shell=True)
        res = res.stdout.read().decode(encoding='GBK')
        return res

    def 启动模拟器(self, order):
        self.读取命令信息('ldconsole.exe launch --index ' + order)

    def 关闭模拟器(self, order):
        self.读取命令信息(cmd='ldconsole.exe quit --index ' + order)

    def 获取模拟器信息(self):
        return self.读取命令信息('ldconsole.exe  list2')
        # 索引，标题，顶层窗口句柄，绑定窗口句柄，是否进入android，进程PID，VBox进程PID

    def 新增模拟器(self, name):
        self.读取命令信息('ldconsole.exe add --name ' + name)

    def 删除模拟器(self, order):
        self.读取命令信息('ldconsole.exe remove --index ' + order)

    def 复制模拟器(self, name, order):
        self.读取命令信息('ldconsole.exe copy --name ' + name + ' --from ' + order)

    def 启动APP(self, order, packagename):
        self.读取命令信息('ldconsole.exe runapp --index ' + order + ' --packagename ' + packagename)

    def 关闭APP(self, order, packagename):
        self.读取命令信息('ldconsole.exe killapp --index ' + order + ' --packagename ' + packagename)

    def 获取包名(self, order):
        return self.读取命令信息(cmd='ld.exe -s ' + order + '  pm list packages')

    def 安装APP(self, order, path):
        self.读取命令信息('ldconsole.exe  installapp --index ' + order + ' --filename ' + path)

    def 排列窗口(self):
        self.读取命令信息('ldconsole.exe sortWnd')

    def 重启(self, order):
        self.读取命令信息('ldconsole.exe reboot --index ' + order)

    def 取指定模拟器游戏句柄(self, order):
        list = self.获取模拟器信息()
        items = list.splitlines()
        return items[int(order)].split(',')[3]


class Memory:
    def __init__(self, dx, hwd):
        self.__dx = dx
        self.hwd = hwd

    def 特征码定位地址(self, s, model, off):
        # 返回16进制字符串地址
        module_size = self.__dx.GetModuleSize(self.hwd, model)
        base_address = self.__dx.GetModuleBaseAddr(self.hwd, model)
        end_address = module_size + base_address
        call_address = self.__dx.FindData(self.hwd, hex(base_address)[2:] + '-' + hex(end_address)[2:], s)
        return hex(int(call_address, 16) + int(off, 16))[2:]

    def 特征码定位基址(self, s, model, off):
        特征码地址 = self.特征码定位地址(s, model, off)
        特征码地址值 = self.__dx.readint(self.hwd, 特征码地址, 4)
        return hex(int(特征码地址, 16) + int(特征码地址值) + 4)[2:]


if __name__ == '__main__':
    dm = RegDm.reg()
    print(dm.ver())
