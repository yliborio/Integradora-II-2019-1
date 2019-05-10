d = dict()
s = ""
def readLog():
    global s
    filename = "logViews"
    with open(filename) as f:
        content = f.readlines()
    for line in content:
        s+=line

def separateWhere(query):
    search = query.split("where")
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
    filename = "colunm"

    with open(filename) as f:
        content = f.readlines()
    k = ""
    for line in content:
        k+=line
    cl = k.split("| ")
    for x in cl:
        for u in x.split(" "):
            d[u] = contColunms(u)
    

if __name__ == "__main__":
    readLog()
    initiateDict()
    hz = 0
    for key in d:
        if d[key] > 0:
            hz+=1
        if(len(key) > 2):
            print(key, d[key])
    print("Used", hz, "columns")
    #print(s)


#talvez utilizar as 20 mais frequentes??? 