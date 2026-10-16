"""Grid based two-layer router for the small control board (prototype only)."""
from collections import defaultdict
from heapq import heappop, heappush
from pathlib import Path
import math
import pcbnew as p

ROOT = Path(__file__).resolve().parent
PATH = ROOT / "control-board.kicad_pcb"
board = p.LoadBoard(str(PATH))
STEP = 0.5
NX, NY = 231, 191
LAYERS = (p.F_Cu, p.B_Cu)
WIDTH = p.FromMM(0.30)

def snap(v): return round(v / STEP)
def xy(item):
    v = item.GetPosition()
    return (p.ToMM(v.x), p.ToMM(v.y))
def grid(item):
    x,y=xy(item)
    return snap(x),snap(y)
def vec(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def at_grid(x,y): return vec(x*STEP,y*STEP)

blocked = defaultdict(set)
pads_by_net = defaultdict(list)
allpads = []
for fp in board.GetFootprints():
    for pad in fp.Pads():
        name=pad.GetNetname()
        x,y=xy(pad)
        sx,sy=pad.GetSize().x,pad.GetSize().y
        radius=max(p.ToMM(sx),p.ToMM(sy))/2+0.80
        allpads.append((x,y,radius,name))
        if name:
            pads_by_net[name].append(pad)

def pad_clear(x,y,net):
    xx,yy=x*STEP,y*STEP
    for px,py,radius,pname in allpads:
        if pname!=net and (xx-px)**2+(yy-py)**2 < radius**2:
            return False
    return True

def legal(x,y,layer,net,via=False):
    if x<5 or x>NX-5 or y<5 or y>NY-5: return False
    xx,yy=x*STEP,y*STEP
    # WROOM antenna zone at the top of the ESP32 carrier.
    if 39<=xx<=75 and 7<=yy<=15: return False
    if not pad_clear(x,y,net): return False
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            names=blocked[(layer,x+dx,y+dy)]
            if names and (names-{net}): return False
    if via:
        for px,py,radius,_ in allpads:
            if (xx-px)**2+(yy-py)**2 < (radius+0.25)**2:
                return False
        for l in LAYERS:
            for dx in (-2,-1,0,1,2):
                for dy in (-2,-1,0,1,2):
                    if dx*dx+dy*dy>5: continue
                    names=blocked[(l,x+dx,y+dy)]
                    if names and (names-{net}): return False
    return True

def astar(a,b,net):
    ax,ay=grid(a); bx,by=grid(b)
    best={(ax,ay,0):0,(ax,ay,1):0}
    parent={}
    heap=[]
    for z in (0,1):
        heappush(heap,(math.hypot(ax-bx,ay-by),0,(ax,ay,z)))
    n=0
    while heap:
        _,cost,state=heappop(heap)
        if cost!=best.get(state): continue
        x,y,z=state
        if (x,y)==(bx,by):
            out=[state]
            while state in parent:
                state=parent[state]; out.append(state)
            out.reverse()
            return out
        n+=1
        if n>500000: break
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
            q=(x+dx,y+dy,z)
            if not legal(q[0],q[1],LAYERS[z],net): continue
            extra=1.4142 if dx and dy else 1
            nc=cost+extra
            if nc<best.get(q,float('inf')):
                best[q]=nc; parent[q]=state
                heappush(heap,(nc+math.hypot(q[0]-bx,q[1]-by),nc,q))
        q=(x,y,1-z)
        if legal(x,y,LAYERS[1-z],net,via=True):
            nc=cost+15
            if nc<best.get(q,float('inf')):
                best[q]=nc;parent[q]=state
                heappush(heap,(nc+math.hypot(x-bx,y-by),nc,q))
    return None

def segment(a,b,layer,net):
    if a==b: return
    t=p.PCB_TRACK(board)
    t.SetStart(vec(*a));t.SetEnd(vec(*b));t.SetWidth(WIDTH)
    t.SetLayer(layer);t.SetNet(board.FindNet(net));board.Add(t)

def add_via(x,y,net):
    if (x,y,net) in used_vias:
        return
    used_vias.add((x,y,net))
    v=p.PCB_VIA(board)
    v.SetPosition(at_grid(x,y));v.SetWidth(p.FromMM(0.8));v.SetDrill(p.FromMM(0.4))
    v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu)
    v.SetNet(board.FindNet(net));board.Add(v)

def record(path,net):
    for x,y,z in path:
        blocked[(LAYERS[z],x,y)].add(net)
    for (x,y,z),(xx,yy,zz) in zip(path,path[1:]):
        if z!=zz:
            for l in LAYERS: blocked[(l,x,y)].add(net)

def lay(path,pad_a,pad_b,net):
    px,py=xy(pad_a); qx,qy=xy(pad_b)
    first=path[0];last=path[-1]
    segment((px,py),(first[0]*STEP,first[1]*STEP),LAYERS[first[2]],net)
    start=first
    prev=first
    direction=None
    for point in path[1:]:
        if point[2]!=prev[2]:
            segment((start[0]*STEP,start[1]*STEP),(prev[0]*STEP,prev[1]*STEP),LAYERS[prev[2]],net)
            add_via(prev[0],prev[1],net)
            start=point; direction=None
        else:
            nd=(point[0]-prev[0],point[1]-prev[1])
            if direction is not None and nd!=direction:
                segment((start[0]*STEP,start[1]*STEP),(prev[0]*STEP,prev[1]*STEP),LAYERS[prev[2]],net)
                start=prev
            direction=nd
        prev=point
    segment((start[0]*STEP,start[1]*STEP),(last[0]*STEP,last[1]*STEP),LAYERS[last[2]],net)
    segment((last[0]*STEP,last[1]*STEP),(qx,qy),LAYERS[last[2]],net)
    record(path,net)

order=["+5V","+3V3","IR32","GND","QR_TX","QR_RX","PWM25","DIR26","FLT27","OPEN34","HOME33",
       "OPTO_ANODE","IR_COM"]
used_vias=set()
failed=[]
for name in order:
    pins=pads_by_net[name]
    if len(pins)<2: continue
    tree=[pins[0]];remaining=pins[1:]
    while remaining:
        pairs=sorted(((math.dist(xy(a),xy(b)),a,b) for a in tree for b in remaining), key=lambda row:row[0])
        path=None;chosen=None
        for _,a,b in pairs:
            path=astar(a,b,name)
            if path is not None:
                chosen=(a,b);break
        if path is None:
            failed.append((name,[p.GetNumber() for p in remaining]))
            break
        a,b=chosen
        lay(path,a,b,name)
        tree.append(b);remaining.remove(b)
    print(name,"routed",len(tree),"of",len(pins))

p.SaveBoard(str(PATH),board)
print("Failed:",failed)
if failed: raise SystemExit(1)
