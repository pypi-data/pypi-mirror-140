class Memory:
    def __init__(self,dx,hwd):
        self.__dx = dx
        self.hwd=hwd
    def 特征码定位地址(self,s,model,off):
        #返回16进制字符串地址
        module_size = self.__dx.GetModuleSize(self.hwd, model)
        base_address = self.__dx.GetModuleBaseAddr(self.hwd, model)
        end_address = module_size + base_address
        call_address = self.__dx.FindData(self.hwd, hex(base_address)[2:] + '-' + hex(end_address)[2:], s).split('|')
        return hex(int(call_address, 16) + int(off,16))[2:]
    def 特征码定位基址 (self,s,model,off):
        特征码地址=self.特征码定位地址(s,model,off)
        特征码地址值=self.__dx.readint(self.hwd,特征码地址,4)
        return hex(int(特征码地址,16)+int(特征码地址值)+4)[2:]

