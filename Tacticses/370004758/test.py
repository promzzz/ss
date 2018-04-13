from TacticsEngine import TacticsEngine

class Tactics(TacticsEngine):
    name = '测试策略2'
    def init(self):
        pass
    def tactics(self, data):
        print(self.name,data)
        print(self.caseEngine.fundPool)
        print(self.caseEngine.userInfo)