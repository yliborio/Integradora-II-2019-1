class States:

    
    def __init__(self, n):
        self.n_MAX = n
        self.d = dict()
        

    tables = {
        'c' :  'customer',
        'l' : 'lineitem',
        'n' : 'nation',
        'o' : 'orders',
        'p' : 'part',
        'ps': 'partsupp',
        'r' : 'region',
        's' : 'supplier'
    }
    def readLog(self):
        s = ""
        filename = "logViews"
        with open(filename) as f:
            content = f.readlines()
        for line in content:
            s += line
        return s

    def separateWhere(self,query):
        search = query.split("from")
        if(len(search) == 1 ):
            return ""
        search = search[1:] # search[0] contem o que veio antes do primeiro 
        res = ""            # where 
        for p in search:
            res+=p
        return res

    t = {
         'customer': ['c_custkey', 'c_nationkey'],
        'lineitem': ['l_orderkey', 'l_linenumber', 'l_partkey', 'l_suppkey'],
         'nation': ['n_nationkey', 'n_regionkey'],
         'orders': ['o_orderkey', 'o_custkey'],
         'part': ['p_partkey'],
         'partsupp': ['ps_partkey', 'ps_suppkey'],
         'region': ['r_regionkey'],
         'supplier': ['s_suppkey', 's_nationkey']
     }

    def contColunms(self,s,col):
        views = s.split("|\n|") #separa as linhas consultas 
        cont = 0
        for query in views:
            result = self.separateWhere(query) # descarta as colunas utilizadas
            if len(result) == 0:          # no select
                continue
            if col in result:
                cont += 1
        return cont


    def initiateDict(self):
        filename = "columns"
        s = self.readLog()
        with open(filename) as f:
            content = f.readlines()
        cl = []
        for line in content:
            cl += [line.replace("|","").replace(" ","").replace('\n',"")]
        for x in cl:
            self.d[x] = self.contColunms(s,x)
        #print(self.d)


    def getUsedAtLeast(self,n):
        res = []
        for x in self.d:
            if self.d[x] < n:
                res += [x]
        return res

    def createStates(self,lst):
        for i in lst:
            key = self.tables[i.split("_")[0]]
            if key not in self.t : self.t[key] = [i] 
            else : self.t[key] += [i]
        return self.t 

    
    def getStates(self):
        self.initiateDict()
        lst = self.getUsedAtLeast(self.n_MAX)
        return self.createStates(lst)

if __name__ == "__main__":
    S = States(3)
    print(S.getStates())
    print(S.d)




    

