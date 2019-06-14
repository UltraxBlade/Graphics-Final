import math

def normalize(v):
    if v==[0,0,0]:
        return v
    mag=0
    for comp in v:
        mag+=comp*comp
    mag=math.sqrt(mag)
    for i in range(len(v)):
        v[i]=v[i]/mag
    return v

def dotProduct(v1,v2):
    ans=0
    for i in range(len(v1)):
        ans+=v1[i]*v2[i]
    return ans

def crossProduct(v1,v2):
    return [v1[1]*v2[2]-v1[2]*v2[1],
        v1[2]*v2[0]-v1[0]*v2[2],
        v1[0]*v2[1]-v1[1]*v2[0]]

def I(n):
    M=[[0 for i in range(n)] for j in range(n)]
    for i in range(n):
        M[i][i]=1
    return M

def printMatrix(M):
    if len(M)>0:
        maxFound=0
        for r in range(len(M)):
            for c in range(len(M[r])):
                if M[r][c]==0:
                    numspaces=0
                elif M[r][c]<0:
                    numspaces=int(math.log10(abs(M[r][c])))+1
                else:
                    numspaces=int(math.log10(M[r][c]))
                if numspaces>maxFound:
                    maxFound=numspaces
        
        for r in range(len(M)):
            for c in range(len(M[r])):
                if M[r][c]==0:
                    numspaces=0
                elif M[r][c]<0:
                    numspaces=int(math.log10(abs(M[r][c])))+1
                else:
                    numspaces=int(math.log10(M[r][c]))
                if numspaces>maxFound:
                    maxFound=numspaces
                print(M[r][c],end=" "*(maxFound-numspaces+1))
            print()

def multMatrix(M1,M2):
    if len(M1[0])!=len(M2):
        return
    M=[[0 for i in range(len(M2[0]))] for j in range(len(M1))]
    for r in range(len(M)):
        for c in range(len(M[r])):
            for i in range(len(M1[0])):
                M[r][c]+=M1[r][i]*M2[i][c]
    return M

def scaleMatrix(n,M):
    newM=[[M[r][c]*n for c in range(len(M[r]))] for r in range(len(M))]
    return newM

def scaleVector(n,v):
    newV=[v[i]*n for i in range(len(v))]
    return newV

def addMatrix(M1,M2):
    newM=[[M1[r][c]+M2[r][c] for c in range(len(M1[r]))] for r in range(len(M1))]
    return newM

def addVector(v1,v2):
    newV=[v1[i]+v2[i] for i in range(len(v1))]
    return newV

def subtractVector(v1,v2):
    newV=[v1[i]-v2[i] for i in range(len(v1))]
    return newV

"""testM=[[-100,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
testM2=scaleMatrix(2,I(4))
printMatrix(testM)
printMatrix(testM2)
printMatrix(I(4))
printMatrix(multMatrix(I(4),testM))
printMatrix(multMatrix(testM2,testM))
printMatrix(multMatrix([[1,2],[2,1]],[[0,4],[1,2]]))"""
