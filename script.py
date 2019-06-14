import mdl
from display import *
from matrix import *
from Graphics import *
import math

class WorldStack:
    def __init__(self):
        self.L=[I(4)]
    def push(self):
        self.L.append([r[:] for r in self.L[len(self.L)-1]])
    def peek(self):
        return self.L[len(self.L)-1]
    def pop(self):
        return self.L.pop(len(self.L)-1)

def parseMesh(fname,polys):
    f=open(fname, "r")
    mesh=f.read().split("\n")
    f.close()
    vertices=[]
    for line in mesh:
        line=line.split()
        if len(line)>0:
            if line[0]=="v":
                for i in range(1,len(line)):
                    line[i]=float(line[i])
                vertices.append(line[1:4])
            elif line[0]=="f":
                for i in range(1,len(line)):
                    line[i]=line[i].split("/")
                    line[i]=int(line[i][0])-1
                for i in range(1,len(line)-2):
                    addPoly(polys,vertices[line[1]][0],vertices[line[1]][1],vertices[line[1]][2],
                                  vertices[line[i+1]][0],vertices[line[i+1]][1],vertices[line[i+1]][2],
                                  vertices[line[i+2]][0],vertices[line[i+2]][1],vertices[line[i+2]][2])

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return
    
    img=generate(501,501)
    zbuff=zbuffer(501,501,501)
    world=WorldStack()
    if "_default" not in symbols:
        symbols['_default'] = ['constants',
                             {'red': [0.2, 0.5, 0.5],
                              'green': [0.2, 0.5, 0.5],
                              'blue': [0.2, 0.5, 0.5]}]
    initialDefault=symbols['_default']
    edgeColor=[0,0,0]
    frames=None
    baseName=None
    shading=None
    vary=[]
    lights=[]
    vertexNorms={}
    for key in symbols.keys():
        if symbols[key][0]=="light":
            light=symbols[key][1]
            light["location"]=normalize(light["location"])
            lights.append(light)
    if len(lights)==0:
        print("No lights given. Creating light at (0.5,0.75,1) with color (255,255,255)")
        lights=[{"location":normalize([0.5,0.75,1]),"color":[255,255,255]}]
    setLights(lights)
    for command in commands:
        #print(command)
        if command["op"]=="shading":
            shading=command["shade_type"]
        if command["op"]=="frames":
            frames=int(command["args"][0])
        if command["op"]=="basename":
            baseName=command["args"][0]
        if command["op"]=="vary":
            vary.append(command)
    if shading==None:
        print("No shading specified. Using flat shading.")
        shading="flat"
    if baseName==None and frames!=None:
        print("No base name given. Setting base name to 'image'.")
        baseName="image"
    #print(shading)
    if frames==None:
        if len(vary)>0:
            print("Error: 'vary' found, but no frame count given")
        else:
            if shading=="gouraud" or shading=="phong":
                world=WorldStack()
                for command in commands:
                    polys=[[],[],[],[]]
                    transform=world.peek()
                    coords=None
                    if command["args"]!=None:
                        coords=command["args"][:]
                    if command["op"]=="push":
                        world.push()
                    elif command["op"]=="pop":
                        world.pop()
                    elif command["op"]=="move":
                        transform=multMatrix(transform,translate(coords[0],coords[1],coords[2]))
                        for r in range(len(world.peek())):
                            world.peek()[r]=transform[r]
                    elif command["op"]=="scale":
                        transform=multMatrix(transform,scale(coords[0],coords[1],coords[2]))
                        for r in range(len(world.peek())):
                            world.peek()[r]=transform[r]
                    elif command["op"]=="rotate":
                        transform=multMatrix(transform,rotate(coords[0],float(coords[1])))
                        for r in range(len(world.peek())):
                            world.peek()[r]=transform[r]
                    elif command["op"]=="triangle":
                        addPoly(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7],coords[8])
                    elif command["op"]=="box":
                        box(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                    elif command["op"]=="sphere":
                        sphere(polys,coords[0],coords[1],coords[2],coords[3])
                    elif command["op"]=="torus":
                        torus(polys,coords[0],coords[1],coords[2],coords[3],coords[4])
                    elif command["op"]=="mesh":
                        parseMesh(command["args"][0],polys)
                    polys=multMatrix(transform,polys)
                    for col in range(0,len(polys[0])-1,3):
                        v1=(int(polys[0][col]*1000)/1000.0,int(polys[1][col]*1000)/1000.0,int(polys[2][col]*1000)/1000.0)
                        v2=(int(polys[0][col+1]*1000)/1000.0,int(polys[1][col+1]*1000)/1000.0,int(polys[2][col+1]*1000)/1000.0)
                        v3=(int(polys[0][col+2]*1000)/1000.0,int(polys[1][col+2]*1000)/1000.0,int(polys[2][col+2]*1000)/1000.0)
                        norm=surfaceNorm(v1,v2,v3)
                        if v1 in vertexNorms.keys():
                            vertexNorms[v1]=normalize(addVector(vertexNorms[v1],norm))
                        else:
                            vertexNorms[v1]=norm
                        if v2 in vertexNorms.keys():
                            vertexNorms[v2]=normalize(addVector(vertexNorms[v2],norm))
                        else:
                            vertexNorms[v2]=norm
                        if v3 in vertexNorms.keys():
                            vertexNorms[v3]=normalize(addVector(vertexNorms[v3],norm))
                        else:
                            vertexNorms[v3]=norm
            #print(shading)
            world=WorldStack()
            setShading(shading,vertexNorms)
            for command in commands:
                #print(command)
                edges=[[],[],[],[]]
                polys=[[],[],[],[]]
                transform=world.peek()
                coords=None
                if command["args"]!=None:
                    coords=command["args"][:]
                if command["op"]=="set_default":
                    if command["constants"]!=None:
                        symbols["_default"]=symbols[command["constants"]]
                    else:
                        symbols["_default"]=['constants',
                                             {'red': [coords[0], coords[1], coords[2]],
                                              'green': [coords[3], coords[4], coords[5]],
                                              'blue': [coords[6], coords[7], coords[8]]}]
                polyColor=symbols["_default"][1]
                if command["op"]=="push":
                    world.push()
                elif command["op"]=="pop":
                    world.pop()
                elif command["op"]=="move":
                    transform=multMatrix(transform,translate(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="scale":
                    transform=multMatrix(transform,scale(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="rotate":
                    transform=multMatrix(transform,rotate(coords[0],float(coords[1])))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="box":
                    box(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="sphere":
                    sphere(polys,coords[0],coords[1],coords[2],coords[3])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="torus":
                    torus(polys,coords[0],coords[1],coords[2],coords[3],coords[4])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="triangle":
                    addPoly(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7],coords[8])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="mesh":
                    #print(command)
                    parseMesh(command["args"][0],polys)
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="line":
                    addEdge(edges,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                elif command["op"]=="save":
                    save_extension(img,command["args"][0])
                elif command["op"]=="display":
                    display(img)
                if len(edges[0])>0:
                    edges=multMatrix(transform,edges)
                    drawLines(img,zbuff,edges,edgeColor)
                if len(polys[0])>0:
                    polys=multMatrix(transform,polys)
                    drawPolys(img,zbuff,polys,polyColor)
    else:
        knobs={}
        for command in vary:
            #print(command)
            if command["knob"] in knobs:
                vals=knobs[command["knob"]]
            else:
                vals=[None]*frames
            dval=command["args"][3]-command["args"][2]
            nframes=command["args"][1]-command["args"][0]
            for i in range(int(command["args"][0]),int(command["args"][1]+1)):
                vals[i]=command["args"][2]+dval*((i-command["args"][0])/nframes)
            knobs[command["knob"]]=vals
        for knob in knobs.keys():
            lastFound=None
            firstFound=None
            vals=knobs[knob]
            for i in range(len(vals)):
                if vals[i]==None:
                    vals[i]=lastFound
                else:
                    if firstFound==None:
                        firstFound=vals[i]
                    lastFound=vals[i]
            for i in range(len(vals)):
                if vals[i]==None:
                    vals[i]=firstFound
            knobs[knob]=vals
        #print(knobs)
        for frame in range(frames):
            if shading=="gouraud" or shading=="phong":
                world=WorldStack()
                for command in commands:
                    polys=[[],[],[],[]]
                    transform=world.peek()
                    coords=None
                    if command["args"]!=None:
                        coords=command["args"][:]
                    if command["op"]=="push":
                        world.push()
                    elif command["op"]=="pop":
                        world.pop()
                    elif command["op"]=="move":
                        if "knob" in command.keys() and command["knob"]!=None:
                            for i in range(len(coords)):
                                coords[i]=coords[i]*knobs[command["knob"]][frame]
                        #print(coords)
                        transform=multMatrix(transform,translate(coords[0],coords[1],coords[2]))
                        for r in range(len(world.peek())):
                            world.peek()[r]=transform[r]
                    elif command["op"]=="scale":
                        if "knob" in command.keys() and command["knob"]!=None:
                            for i in range(len(coords)):
                                coords[i]=coords[i]*knobs[command["knob"]][frame]
                        #print(coords)
                        transform=multMatrix(transform,scale(coords[0],coords[1],coords[2]))
                        for r in range(len(world.peek())):
                            world.peek()[r]=transform[r]
                    elif command["op"]=="rotate":
                        if "knob" in command.keys() and command["knob"]!=None:
                            coords[1]=coords[1]*knobs[command["knob"]][frame]
                        #print(coords)
                        transform=multMatrix(transform,rotate(coords[0],float(coords[1])))
                        for r in range(len(world.peek())):
                            world.peek()[r]=transform[r]
                    elif command["op"]=="triangle":
                        addPoly(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7],coords[8])
                    elif command["op"]=="box":
                        box(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                    elif command["op"]=="sphere":
                        sphere(polys,coords[0],coords[1],coords[2],coords[3])
                    elif command["op"]=="torus":
                        torus(polys,coords[0],coords[1],coords[2],coords[3],coords[4])
                    elif command["op"]=="mesh":
                        parseMesh(command["args"][0],polys)
                    polys=multMatrix(transform,polys)
                    for col in range(0,len(polys[0])-1,3):
                        v1=(int(polys[0][col]*1000)/1000.0,int(polys[1][col]*1000)/1000.0,int(polys[2][col]*1000)/1000.0)
                        v2=(int(polys[0][col+1]*1000)/1000.0,int(polys[1][col+1]*1000)/1000.0,int(polys[2][col+1]*1000)/1000.0)
                        v3=(int(polys[0][col+2]*1000)/1000.0,int(polys[1][col+2]*1000)/1000.0,int(polys[2][col+2]*1000)/1000.0)
                        norm=surfaceNorm(v1,v2,v3)
                        if v1 in vertexNorms.keys():
                            vertexNorms[v1]=normalize(addVector(vertexNorms[v1],norm))
                        else:
                            vertexNorms[v1]=norm
                        if v2 in vertexNorms.keys():
                            vertexNorms[v2]=normalize(addVector(vertexNorms[v2],norm))
                        else:
                            vertexNorms[v2]=norm
                        if v3 in vertexNorms.keys():
                            vertexNorms[v3]=normalize(addVector(vertexNorms[v3],norm))
                        else:
                            vertexNorms[v3]=norm
            img=generate(501,501)
            zbuff=zbuffer(501,501,501)
            world=WorldStack()
            symbols["_default"]=initialDefault
            setShading(shading,vertexNorms)
            for command in commands:
                #print(command)
                edges=[[],[],[],[]]
                polys=[[],[],[],[]]
                transform=world.peek()
                coords=None
                if command["args"]!=None:
                    coords=command["args"][:]
                #print(coords)
                if command["op"]=="set_default":
                    if command["constants"]!=None:
                        symbols["_default"]=symbols[command["constants"]]
                    else:
                        symbols["_default"]=['constants',
                                             {'red': [coords[0], coords[1], coords[2]],
                                              'green': [coords[3], coords[4], coords[5]],
                                              'blue': [coords[6], coords[7], coords[8]]}]
                polyColor=symbols["_default"][1]
                if command["op"]=="push":
                    world.push()
                elif command["op"]=="pop":
                    world.pop()
                elif command["op"]=="move":
                    if "knob" in command.keys() and command["knob"]!=None:
                        for i in range(len(coords)):
                            coords[i]=coords[i]*knobs[command["knob"]][frame]
                    #print(coords)
                    transform=multMatrix(transform,translate(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="scale":
                    if "knob" in command.keys() and command["knob"]!=None:
                        for i in range(len(coords)):
                            coords[i]=coords[i]*knobs[command["knob"]][frame]
                    #print(coords)
                    transform=multMatrix(transform,scale(coords[0],coords[1],coords[2]))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="rotate":
                    if "knob" in command.keys() and command["knob"]!=None:
                        coords[1]=coords[1]*knobs[command["knob"]][frame]
                    #print(coords)
                    transform=multMatrix(transform,rotate(coords[0],float(coords[1])))
                    for r in range(len(world.peek())):
                        world.peek()[r]=transform[r]
                elif command["op"]=="box":
                    box(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="sphere":
                    sphere(polys,coords[0],coords[1],coords[2],coords[3])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="torus":
                    torus(polys,coords[0],coords[1],coords[2],coords[3],coords[4])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="mesh":
                    #print(command)
                    parseMesh(command["args"][0],polys)
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="triangle":
                    addPoly(polys,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5],coords[6],coords[7],coords[8])
                    if command["constants"]!=None:
                        polyColor=symbols[command["constants"]][1]
                elif command["op"]=="line":
                    addEdge(edges,coords[0],coords[1],coords[2],coords[3],coords[4],coords[5])
                elif command["op"]=="save":
                    save_extension(img,command["args"][0])
                elif command["op"]=="display":
                    display(img)
                if len(edges[0])>0:
                    edges=multMatrix(transform,edges)
                    drawLines(img,zbuff,edges,edgeColor)
                if len(polys[0])>0:
                    polys=multMatrix(transform,polys)
                    drawPolys(img,zbuff,polys,polyColor)
                if frame==0:
                    numZeroes=int(math.log10(frames))
                else:
                    numZeroes=int(math.log10(frames))-int(math.log10(frame))
            #print(frame)
            save_extension(img,"anim/"+baseName+("0"*numZeroes)+str(frame)+".png")
        make_animation(baseName)
