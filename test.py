d = dict()
s = ""

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
def readLog():
    global s
    filename = "logViews"
    with open(filename) as f:
        content = f.readlines()
    for line in content:
        s+=line

def separateWhere(query):
    search = query.split("from")
    if(len(search) == 1 ):
        return ""
    search = search[1:] # search[0] contem o que veio antes do primeiro 
    res = ""            # where 
    for p in search:
        res+=p
    return res


def contColunms(col):
    global s
    views = s.split("|\n|") #separa as linhas consultas 
    cont = 0
    for query in views:
        result = separateWhere(query) # descarta as colunas utilizadas
        if len(result) == 0:          # no select
            continue
        ax = result.split("`") # cada coluna esta entre "`"s
        for y in ax:           # ex: `l_lineitem`
           if col in y:
               cont+=1
    return cont


def initiateDict():
    filename = "columns"

    with open(filename) as f:
        content = f.readlines()
    cl = []
    for line in content:
        cl += [line.replace("|","").replace(" ","").replace('\n',"")]
    for x in cl:
        d[x] = contColunms(x)


def getUsedAtLeast(n):
    res = []
    for x in d:
        if d[x] >= n:
            res += [x]
    return res

def createStates(lst):
    t = dict()
    for i in lst:
        key = tables[i.split("_")[0]]
        if key not in t: t[key] = [i] 
        else : t[key] += [i]
    return t 

    
if __name__ == "__main__":
    readLog()
    initiateDict()
    hz = 0
    for key in d:
        if d[key] > 0:
            hz+=1
        print(key, d[key])
    print("Used", hz, "columns")
    lst = getUsedAtLeast(3)
    print(createStates(lst))



    