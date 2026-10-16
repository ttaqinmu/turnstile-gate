"""Procedural turnstile hardware concept for Blender 5.2.

Run in Blender's Python console or via Blender MCP. Units are metres.
The PCB and electronics are deliberately simplified; mechanical parts are detailed.
"""
import bpy
import math
from mathutils import Vector

OUT = "/home/muttaqin/turnstile-gate/hardware.blend"

# Start a clean scene, keeping the result reproducible.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablock in list(bpy.data.collections):
    if datablock != bpy.context.scene.collection:
        bpy.data.collections.remove(datablock)

def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

COL = {name: collection(name) for name in [
    "01 Pedestal and frame", "02 Drive motor and gearbox", "03 Gears and shaft",
    "04 Swing leaf", "05 Bearings and limit switches", "06 QR IR and dummy PCB",
    "07 Fasteners and wiring", "08 Stage and lighting", "09 Removable gear cover",
    "10 Lower enclosure shell",
]}

def put(obj, group):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL[group].objects.link(obj)
    return obj

def mat(name, rgb, metal=0.0, rough=0.4):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    return m

M={
    "frame":mat("Powder coated graphite",(.055,.070,.082),.65,.28),
    "steel":mat("Machined stainless steel",(.55,.61,.64),.88,.22),
    "steel_dark":mat("Dark hardened shaft steel",(.16,.19,.22),.82,.24),
    "brass":mat("Gear bronze",(.72,.43,.13),.82,.28),
    "gear":mat("Hardened gear steel",(.35,.41,.45),.85,.25),
    "motor":mat("Motor shell blue gray",(.13,.20,.25),.65,.31),
    "motor_cap":mat("Motor end cap",(.09,.11,.13),.55,.34),
    "rubber":mat("Black rubber",(.018,.022,.025),.05,.75),
    "glass":mat("Acrylic gate panel",(.16,.58,.67),.13,.21),
    "green":mat("PCB solder mask",(.025,.24,.13),.08,.55),
    "copper":mat("PCB copper pads",(.71,.48,.14),.80,.30),
    "screen":mat("Scanner glass",(.012,.035,.055),.08,.14),
    "service_window":mat("Smoked polycarbonate service door",(.10,.19,.22),.05,.22),
    "white":mat("Printed white",(.82,.88,.86),0,.7),
    "red":mat("IR emitter red",(.8,.035,.025),.05,.23),
    "cable_red":mat("Cable red",(.54,.045,.034),0,.58),
    "cable_black":mat("Cable black",(.025,.027,.030),0,.6),
    "cable_blue":mat("Cable blue",(.045,.20,.50),0,.58),
    "floor":mat("Display floor",(.19,.22,.25),.05,.7),
}
service_bs=next(n for n in M["service_window"].node_tree.nodes if n.type=="BSDF_PRINCIPLED")
service_bs.inputs["Alpha"].default_value=.16
M["service_window"].diffuse_color=(.10,.19,.22,.16)
methods=[i.identifier for i in M["service_window"].bl_rna.properties["surface_render_method"].enum_items]
if "BLENDED" in methods:
    M["service_window"].surface_render_method="BLENDED"
glass_bs=next(n for n in M["glass"].node_tree.nodes if n.type=="BSDF_PRINCIPLED")
glass_bs.inputs["Alpha"].default_value=.24
M["glass"].diffuse_color=(.16,.58,.67,.24)
if "BLENDED" in methods:
    M["glass"].surface_render_method="BLENDED"

def shade(obj):
    if obj.type == "MESH":
        for f in obj.data.polygons: f.use_smooth=True
    return obj

def box(name, loc, dims, material, group, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Machined edges", "BEVEL")
        mod.width=bevel; mod.segments=3
        o.modifiers.new("Weighted face normals", "WEIGHTED_NORMAL")
    return put(o,group)

def cyl(name, loc, radius, depth, material, group, verts=48, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    shade(o)
    if bevel:
        mod=o.modifiers.new("Edge rounding","BEVEL")
        mod.width=bevel;mod.segments=3
        o.modifiers.new("Weighted face normals","WEIGHTED_NORMAL")
    return put(o,group)

def torus(name, loc, major, minor, material, group):
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=12,
        location=loc, major_radius=major, minor_radius=minor)
    o=bpy.context.object;o.name=name;o.data.materials.append(material);shade(o)
    return put(o,group)

def path(name, points, radius, material, group):
    cu=bpy.data.curves.new(name,"CURVE");cu.dimensions="3D"
    cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new("POLY");sp.points.add(len(points)-1)
    for p,xyz in zip(sp.points,points):p.co=(*xyz,1)
    o=bpy.data.objects.new(name,cu);COL[group].objects.link(o)
    o.data.materials.append(material)
    return o

def text(name, body, loc, size, material, group, rotation=(0,0,0)):
    cu=bpy.data.curves.new(name,"FONT");cu.body=body;cu.size=size;cu.extrude=.0005
    o=bpy.data.objects.new(name,cu);COL[group].objects.link(o)
    o.location=loc;o.rotation_euler=rotation;cu.materials.append(material)
    return o

def bolt(name, loc, radius=.006, material=None, group="07 Fasteners and wiring", parent=None):
    material=material or M["steel"]
    h=cyl(name+" head",loc,radius,.004,material,group,16,.0006)
    # A dark slot makes each fastener readable at close range.
    slot=box(name+" slot",(loc[0],loc[1],loc[2]+.0022),
             (radius*1.35,.0012,.0004),M["rubber"],group)
    if parent:
        h.parent=parent;slot.parent=parent
    return h

def gear(name, center, teeth, pitch_r, root_r, tip_r, thick, material, parent=None,
         bore_r=0.0):
    outline=[]
    step=2*math.pi/teeth
    for i in range(teeth):
        c=i*step
        for off,r in [(-.50,root_r),(-.32,root_r),(-.19,pitch_r),
                      (-.10,tip_r),(.10,tip_r),(.19,pitch_r),(.32,root_r)]:
            a=c+off*step
            outline.append((r*math.cos(a),r*math.sin(a)))
    n=len(outline);v=[]
    for z in (-thick/2,thick/2):
        v += [(x,y,z) for x,y in outline]
    if bore_r:
        for z in (-thick/2,thick/2):
            v += [(bore_r*x/math.hypot(x,y),bore_r*y/math.hypot(x,y),z)
                  for x,y in outline]
        faces=[]
        for i in range(n):
            j=(i+1)%n
            faces.extend(((i,j,2*n+j,2*n+i),
                          (n+i,3*n+i,3*n+j,n+j),
                          (2*n+i,2*n+j,3*n+j,3*n+i)))
    else:
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);COL["03 Gears and shaft"].objects.link(o)
    o.location=center;o.data.materials.append(material)
    mod=o.modifiers.new("Deburred teeth","BEVEL")
    mod.width=.0012;mod.segments=2
    o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    if parent:o.parent=parent
    return o

# Open-frame housing: two rounded end posts, a hollow lower drive beam and a
# shallow upper beam. The gear housing is now part of the beam silhouette.
FRAME_X=.26
FRAME_W=.38
FRAME_LENGTH=.90
SHELL="10 Lower enclosure shell"
box("Continuous lower plinth",(FRAME_X,0,.03),(FRAME_W,.94,.06),M["frame"],
    "01 Pedestal and frame",.014)
for x,side in ((.07,"Outer"),(.45,"Lane")):
    box(side+" lower beam skin",(x,0,.20),(.012,.90,.30),M["frame"],SHELL,.005)
    if side=="Outer":
        box(side+" upper beam skin",(x,0,1.165),(.012,.90,.13),M["frame"],SHELL,.006)
    else:
        # One sealed flush window exposes the optics of the internal IR module.
        for y,length in ((-.31,.28),(.19,.52)):
            box("Lane upper beam skin beside IR window",(x,y,1.165),
                (.012,length,.13),M["frame"],SHELL,.006)
        for z,height in ((1.1175,.035),(1.21,.04)):
            box("Lane upper beam skin above or below IR window",(x,-.12,z),
                (.012,.10,height),M["frame"],SHELL,.004)
        box("Flush IR optical window",(.449,-.12,1.1625),(.010,.10,.055),
            M["screen"],SHELL,.002)
for y,end in ((-.45,"Front"),(.45,"Rear")):
    box(end+" lower beam cap",(FRAME_X,y,.20),(FRAME_W,.012,.30),M["frame"],SHELL,.006)
    box(end+" upper beam cap",(FRAME_X,y,1.165),(FRAME_W,.012,.13),M["frame"],SHELL,.006)
    box(end+" integral upright",(.195,y* .8444,.725),(.25,.14,.79),
        M["frame"],SHELL,.012)
# Split the beam roofs around the shaft rather than covering the bearing.
for z,kind in ((.35,"Lower roof"),(1.10,"Upper underside")):
    for x,w in ((.195,.25),(.425,.05)):
        box(kind+" side plate",(x,0,z),(w,.90,.014),M["frame"],SHELL,.004)
    for y in (-.2475,.2475):
        box(kind+" shaft return",(.36,y,z),(.08,.405,.014),M["frame"],SHELL,.004)
box("Sealed continuous upper roof",(FRAME_X,0,1.23),
    (FRAME_W,FRAME_LENGTH,.014),M["frame"],SHELL,.009)
# Flush access panel on the long outside face of the lower drive beam.
box("Flush lower service panel",(.061,0,.195),(.006,.57,.245),
    M["steel_dark"],SHELL,.002)
box("Upper bearing tie bracket",(.36,0,1.18),(.17,.075,.025),M["steel_dark"],
    "01 Pedestal and frame",.004)
for x in (.31,.40):
    bolt("Upper bearing bracket bolt",(x,0,1.194),.0045)
# A slim shaft sleeve visually joins the two beams without a side gearbox pod.
for z,height in ((.425,.15),(.785,.37),(1.085,.03)):
    cyl("Integrated hinge sleeve",(.36,0,z),.026,height,M["steel_dark"],SHELL,64,.002)
for x in (.11,.40):
    for y in (-.38,.38):
        bolt("Plinth anchor",(x,y,.061),.007)

# Pivot empty is the 90 degree animation rig.
rig=bpy.data.objects.new("Swing axis | 0 to 90 deg",None)
COL["04 Swing leaf"].objects.link(rig);rig.location=(0,0,0)

# One bearing in each beam supports the shaft; the former middle block was
# redundant in the open aperture.
for position,z in (("Lower",.12),("Upper",1.18)):
    cyl(position+" shaft bearing block",(0,0,z),.061,.044,M["steel_dark"],
        "05 Bearings and limit switches",64,.004)
    torus(position+" shaft bearing race",(0,0,z+.023),.037,.004,M["steel"],
          "05 Bearings and limit switches")
    for a in range(4):
        t=2*math.pi*a/4+math.pi/4
        bolt(position+" bearing cap screw",
             (.047*math.cos(t),.047*math.sin(t),z+.024),.004)
shaft=cyl("Vertical swing shaft Ø40",(0,0,.66),.020,1.10,M["steel"],"03 Gears and shaft",64,.002)
shaft.parent=rig
torus("Upper beam underside shaft seal",(0,0,1.096),.028,.005,M["rubber"],
      "05 Bearings and limit switches")
top_nut=cyl("Rotating shaft top nut",(0,0,1.210),.030,.017,M["steel_dark"],
            "03 Gears and shaft",48,.002)
top_nut.parent=rig
for z in (.34,.75,1.11):
    col=cyl("Shaft retaining collar",(0,0,z),.030,.020,M["steel_dark"],"03 Gears and shaft",64,.002)
    col.parent=rig

# Motor / gearbox: nominal 24 V DC, vertical output, reduction represented by meshing spurs.
MX=-.162
motor=cyl("24 V DC brushed motor body",(MX,0,.225),.064,.185,M["motor"],"02 Drive motor and gearbox",64,.008)
for z in (.155,.174,.193,.212,.231,.250,.269):
    torus("Motor cooling rib",(MX,0,z),.064,.0036,M["steel_dark"],"02 Drive motor and gearbox")
cyl("Motor rear cap",(MX,0,.129),.068,.025,M["motor_cap"],"02 Drive motor and gearbox",64,.003)
cyl("Motor front cap",(MX,0,.324),.068,.027,M["steel"],"02 Drive motor and gearbox",64,.003)
for a in range(4):
    t=math.pi/4+a*math.pi/2
    bolt("Motor tie rod head",(MX+.052*math.cos(t),.052*math.sin(t),.339),.004)
box("Reduction gearbox casting",(MX,0,.365),(.150,.145,.058),M["steel_dark"],"02 Drive motor and gearbox",.012)
for x in (MX-.058,MX+.058):
    for y in (-.052,.052):
        bolt("Gearbox lid bolt",(x,y,.396),.005)
box("Motor terminal block",(MX,-.070,.234),(.050,.025,.040),M["rubber"],"02 Drive motor and gearbox",.003)
for dx,material in [(-.014,M["cable_red"]),(.014,M["cable_black"])]:
    path("Motor lead",[(MX+dx,-.080,.235),(MX+dx,-.12,.27),
        (MX+dx,-.13,.47),(MX+dx,-.18,.56)],.0028,material,"07 Fasteners and wiring")
text("Motor rating label","24 V DC  |  GEARMOTOR",(MX-.066,-.066,.215),.009,
     M["white"],"02 Drive motor and gearbox",(math.pi/2,0,0))

pinion_shaft=cyl("Gearbox output shaft",(MX,0,.445),.014,.11,M["steel"],"03 Gears and shaft",48,.001)
pinion=gear("14 tooth drive pinion",(MX,0,.480),14,.042,.035,.049,.040,M["gear"])
pinion_hub=cyl("Pinion hub",(MX,0,.507),.027,.020,M["steel_dark"],"03 Gears and shaft",48,.002)
# Both are rotationally symmetric and share the pinion centre without parenting.
large=gear("40 tooth output gear",(0,0,.480),40,.120,.113,.127,.043,
           M["brass"],rig,bore_r=.036)
sleeve=cyl("Splined output shaft sleeve",(0,0,.480),.030,.160,M["steel_dark"],
           "03 Gears and shaft",64,.002)
sleeve.parent=rig
for a in range(12):
    angle=2*math.pi*a/12
    tooth=box("Sleeve spline tooth",(.033*math.cos(angle),.033*math.sin(angle),.480),
              (.008,.006,.080),M["steel"],"03 Gears and shaft",.001)
    tooth.rotation_euler[2]=angle
    tooth.parent=rig
hub=cyl("Output gear central hub",(0,0,.511),.055,.034,M["steel_dark"],"03 Gears and shaft",64,.004)
hub.parent=rig
for a in range(8):
    t=2*math.pi*a/8
    bolt("Output gear retaining screw",(.080*math.cos(t),.080*math.sin(t),.503),.0048,parent=rig)
for a in range(4):
    t=2*math.pi*a/4+math.pi/4
    cyl("Gear web relief",(.070*math.cos(t),.070*math.sin(t),.503),.010,.002,
        M["steel_dark"],"03 Gears and shaft",32,.001).parent=rig

# Swing leaf: clear pane with only two short metal hinge clamps and a soft edge.
for z in (.55,1.02):
    collar=cyl("Hinge knuckle",(0,0,z),.030,.080,M["steel"],"04 Swing leaf",64,.004)
    collar.parent=rig
    for a in (0,math.pi):
        b=bolt("Hinge clamp",(.024*math.cos(a),.024*math.sin(a),z+.041),.004,parent=rig)
for z in (.55,1.02):
    bar=box("Leaf hinge clamp",(.13,0,z),(.20,.043,.036),M["steel"],"04 Swing leaf",.008)
    bar.parent=rig
panel=box("Gate panel acrylic",(.485,0,.78),(.765,.018,.56),M["glass"],"04 Swing leaf",.010)
panel.parent=rig
edge=box("Soft leading safety edge",(.876,0,.78),(.012,.025,.56),M["rubber"],"04 Swing leaf",.004)
edge.parent=rig
for x in (.14,.20):
    for z in (.55,1.02):
        b=bolt("Panel retaining bolt",(x,-.025,z),.004,parent=rig)

# The two limit switches and hard stops sit below the beam roof. Their names
# identify the 0/90 degree positions in Blender; no exterior text is needed.
for name,angle in [("HOME 0°",0),("OPEN 90°",math.pi/2)]:
    r=.055
    x,y=r*math.cos(angle),r*math.sin(angle)
    body=box(name+" microswitch",(x,y,.320),(.035,.022,.018),M["motor_cap"],
             "05 Bearings and limit switches",.002)
    body.rotation_euler[2]=angle
    cyl(name+" roller",(.038*math.cos(angle),.038*math.sin(angle),.331),
        .006,.008,M["steel"],"05 Bearings and limit switches",24,.001)
    stop=box(name+" hard stop",(.068*math.cos(angle),.068*math.sin(angle),.298),
             (.018,.020,.017),M["steel_dark"],"05 Bearings and limit switches",.002)
    stop.rotation_euler[2]=angle

# External electronics are visual placeholders only.
box("QR reader mounting stalk",(-.235,-.090,1.302),(.035,.045,.060),M["steel"],
    "06 QR IR and dummy PCB",.004)
box("QR reader angled enclosure",(-.235,-.113,1.367),(.164,.112,.125),M["motor_cap"],
    "06 QR IR and dummy PCB",.012)
box("QR reader front bezel",(-.235,-.171,1.367),(.139,.005,.101),M["steel_dark"],
    "06 QR IR and dummy PCB",.006)
box("QR optical scan window",(-.235,-.175,1.374),(.075,.003,.069),M["screen"],
    "06 QR IR and dummy PCB",.003)
qr_lens=cyl("QR imager lens",(-.235,-.179,1.374),.017,.005,M["glass"],
            "06 QR IR and dummy PCB",48,.001)
qr_lens.rotation_euler[0]=math.pi/2
for sx in (-.282,-.188):
    for sz in (1.339,1.409):
        led=cyl("QR illumination LED",(sx,-.177,sz),.0048,.003,M["white"],
                "06 QR IR and dummy PCB",24,.0005)
        led.rotation_euler[0]=math.pi/2
cyl("QR read-status indicator",(-.171,-.177,1.324),.005,.003,M["green"],
    "06 QR IR and dummy PCB",24,.0005).rotation_euler[0]=math.pi/2
text("QR reader label","QR SCAN",(-.283,-.178,1.313),.012,M["white"],
     "06 QR IR and dummy PCB",(math.pi/2,0,0))

# Reflective IR emitter and receiver share one module inside the upper beam.
# Only the two small optical faces show through its flush lane-side window.
ir_module=box("IR reflective module inside upper beam",(.409,-.12,1.1625),
              (.052,.086,.050),M["motor_cap"],"06 QR IR and dummy PCB",.004)
ir_module["sensing_mode"]="reflective IR across lane"
for name,y,material in (("IR transmitter",-.142,M["red"]),
                        ("IR receiver",-.098,M["screen"])):
    box(name+" internal diode",(.438,y,1.1625),(.012,.020,.020),
        material,"06 QR IR and dummy PCB",.002)
    optic=cyl(name+" flush optic",(.454,y,1.1625),.006,.003,
              material,"06 QR IR and dummy PCB",32,.001)
    optic.rotation_euler[1]=math.pi/2

# Simplified vertical board mounted to the back panel.
pcb=box("Dummy ESP32 control PCB",(-.175,.177,.73),(.115,.006,.095),M["green"],
        "06 QR IR and dummy PCB",.003)
box("Dummy ESP32 module",(-.18,.169,.735),(.055,.009,.048),M["motor_cap"],
    "06 QR IR and dummy PCB",.003)
for x in (-.216,-.198,-.180,-.162,-.144):
    box("Dummy header",(x,.163,.758),(.004,.003,.004),M["copper"],
        "06 QR IR and dummy PCB",.0005)
for x in (-.226,-.206,-.186,-.166):
    box("Dummy terminal",(x,.164,.694),(.012,.012,.012),M["cable_blue"],
        "06 QR IR and dummy PCB",.002)
text("PCB marker","CTRL PCB",(-.223,.160,.716),.008,M["white"],
     "06 QR IR and dummy PCB",(math.pi/2,0,0))

# Presentation ground and scale references.
box("Neutral floor",(.30,0,-.020),(2.70,1.80,.035),M["floor"],"08 Stage and lighting",.003)
text("Model note","TURNSTILE GATE / 1 LEAF / 90 DEG",(-.70,-.71,.002),.042,
     M["white"],"08 Stage and lighting")

# Scale the motor and reduction into the hollow lower beam. The hinge axis
# stays just outside the inset end posts to clear them throughout the swing.
PIVOT_X=.36
DRIVE_SCALE=.55
GEAR_Z=.25
def drive_z(z):
    return GEAR_Z+DRIVE_SCALE*(z-.480)
def compact_drive_object(ob):
    old=ob.location.copy()
    ob.location.x=(0 if ob.parent==rig else PIVOT_X)+DRIVE_SCALE*old.x
    ob.location.y=DRIVE_SCALE*old.y
    ob.location.z=drive_z(old.z)
    ob.scale*=DRIVE_SCALE

rig.location.x=PIVOT_X
for ob in COL["02 Drive motor and gearbox"].objects:
    compact_drive_object(ob)
for ob in COL["03 Gears and shaft"].objects:
    if ob.name.startswith(("Vertical swing shaft", "Rotating shaft top nut",
                           "Shaft retaining collar")):
        if ob.parent is None: ob.location.x+=PIVOT_X
    else:
        compact_drive_object(ob)
for ob in COL["05 Bearings and limit switches"].objects:
    ob.location.x+=PIVOT_X
for ob in COL["07 Fasteners and wiring"].objects:
    if ob.name.startswith(("Motor tie rod head", "Gearbox lid bolt",
                           "Output gear retaining screw")):
        compact_drive_object(ob)
    elif ob.name.startswith("Motor lead"):
        for spline in ob.data.splines:
            for point in spline.points:
                point.co.x=PIVOT_X+DRIVE_SCALE*point.co.x
                point.co.y=DRIVE_SCALE*point.co.y
                point.co.z=drive_z(point.co.z)
    elif " bearing cap screw" in ob.name:
        ob.location.x+=PIVOT_X
for ob in COL["06 QR IR and dummy PCB"].objects:
    if ob.name.startswith("QR "):
        ob.location.x+=.495
        ob.location.y-=.16
        ob.location.z-=.065
    elif ob.name.startswith("IR "):
        # The complete IR module was placed directly in upper-beam coordinates.
        pass
    else:
        ob.location.x+=.335
        ob.location.z-=.530

# This removable internal shield sits over the gears inside the lower enclosure.
# Its small inboard slot permits engagement with the motor pinion.
def annular_cover(name,z,inner_radius,outer_radius=.153*DRIVE_SCALE,
                  thickness=.008*DRIVE_SCALE,group="09 Removable gear cover"):
    segments=96
    vertices=[]
    for height in (z-thickness/2,z+thickness/2):
        for radius in (inner_radius,outer_radius):
            vertices += [(PIVOT_X+radius*math.cos(2*math.pi*i/segments),
                          radius*math.sin(2*math.pi*i/segments),height)
                         for i in range(segments)]
    faces=[]
    for i in range(segments):
        j=(i+1)%segments
        faces.extend(((i,j,segments+j,segments+i),
                      (2*segments+i,3*segments+i,3*segments+j,2*segments+j),
                      (segments+i,segments+j,3*segments+j,3*segments+i),
                      (i,2*segments+i,2*segments+j,j)))
    mesh=bpy.data.meshes.new(name+" mesh")
    mesh.from_pydata(vertices,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    COL[group].objects.link(ob)
    ob.data.materials.append(M["frame"])
    bevel=ob.modifiers.new("Cover edge radius","BEVEL")
    bevel.width=.0015;bevel.segments=2
    ob.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return ob
annular_cover("Lower beam flush shaft seal plate",.351,.028,.075,.004,SHELL)
annular_cover("Upper beam flush shaft seal plate",1.099,.028,.075,.004,SHELL)
annular_cover("Gear pod opaque bottom",drive_z(.424),.026)
annular_cover("Gear pod removable opaque lid",drive_z(.547),.036)
torus("Gear pod shaft seal",(PIVOT_X,0,drive_z(.552)),.030,.006,M["rubber"],
      "09 Removable gear cover")
for z in (drive_z(.433),drive_z(.538)):
    points=[(PIVOT_X+.150*DRIVE_SCALE*math.cos(math.radians(a)),
             .150*DRIVE_SCALE*math.sin(math.radians(a)),z) for a in range(-160,161,4)]
    path("Gear pod curved perimeter",points,.004*DRIVE_SCALE,M["steel"],
         "09 Removable gear cover")
arc=list(range(-160,161,4))
verts=[(PIVOT_X+.150*DRIVE_SCALE*math.cos(math.radians(a)),
        .150*DRIVE_SCALE*math.sin(math.radians(a)),z)
       for z in (drive_z(.433),drive_z(.538)) for a in arc]
n=len(arc)
faces=[(i,i+1,n+i+1,n+i) for i in range(n-1)]
mesh=bpy.data.meshes.new("Gear pod steel wall mesh")
mesh.from_pydata(verts,[],faces);mesh.update()
wall=bpy.data.objects.new("Gear pod opaque curved wall",mesh)
COL["09 Removable gear cover"].objects.link(wall)
wall.data.materials.append(M["frame"])
wall.modifiers.new("Sheet metal thickness","SOLIDIFY").thickness=.004*DRIVE_SCALE
for a in (-150,-90,-30,30,90,150):
    x=PIVOT_X+.150*DRIVE_SCALE*math.cos(math.radians(a))
    y=.150*DRIVE_SCALE*math.sin(math.radians(a))
    cyl("Gear pod upright",(x,y,drive_z(.485)),.004*DRIVE_SCALE,
        .105*DRIVE_SCALE,M["steel_dark"],
        "09 Removable gear cover",24,.001)
for a in (-105,-35,35,105):
    t=math.radians(a)
    bolt("Gear pod cover screw",(PIVOT_X+.136*DRIVE_SCALE*math.cos(t),
                                  .136*DRIVE_SCALE*math.sin(t),drive_z(.552)),.0035,
         group="09 Removable gear cover")

# 90-degree open/close cycle. Leaf and output gear share the vertical shaft.
scene=bpy.context.scene
for frame,deg in [(1,0),(48,90),(80,90),(128,0)]:
    rig.rotation_euler[2]=math.radians(deg)
    rig.keyframe_insert(data_path="rotation_euler",frame=frame)
    pinion.rotation_euler[2]=-math.radians(deg*40/14)
    pinion.keyframe_insert(data_path="rotation_euler",frame=frame)
scene.frame_start=1;scene.frame_end=128;scene.frame_set(1)
for fc in (rig.animation_data.action.fcurves if hasattr(rig.animation_data.action,"fcurves") else []):
    for k in fc.keyframe_points:k.interpolation="BEZIER"

# Studio camera and lighting.
bpy.ops.object.camera_add(location=(1.75,-2.35,1.55))
cam=bpy.context.object;cam.name="Camera | service-side isometric"
direction=Vector((.24,0,.59))-cam.location
cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO";cam.data.ortho_scale=2.55
scene.camera=cam;put(cam,"08 Stage and lighting")
bpy.ops.object.camera_add(location=(1.35,2.45,1.55))
rear_cam=bpy.context.object;rear_cam.name="Camera | closed rear enclosure"
rear_cam.rotation_euler=(Vector((.18,0,.64))-rear_cam.location).to_track_quat("-Z","Y").to_euler()
rear_cam.data.type="ORTHO";rear_cam.data.ortho_scale=2.40
put(rear_cam,"08 Stage and lighting")
def area(name,loc,power,size):
    data=bpy.data.lights.new(name,"AREA");data.energy=power;data.shape="DISK";data.size=size
    ob=bpy.data.objects.new(name,data);COL["08 Stage and lighting"].objects.link(ob)
    ob.location=loc
    ob.rotation_euler=(Vector((.15,0,.55))-ob.location).to_track_quat("-Z","Y").to_euler()
area("Key softbox",(1.2,-1.1,2.9),850,2.0)
area("Fill softbox",(-1.1,-.3,1.7),430,1.6)
area("Rim softbox",(.9,1.2,2.2),700,1.8)
scene.render.resolution_x=1600;scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.color=(.18,.18,.18)
scene.unit_settings.system="METRIC"
scene.unit_settings.scale_length=1.0

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("Saved",OUT,"objects",len(scene.objects),"meshes",sum(o.type=="MESH" for o in scene.objects))
