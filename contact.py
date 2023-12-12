from pygame.math import Vector2
from physics_objects import *

# Returns a new contact object of the correct subtype
# This function has been done for you.
def generate(a, b, **kwargs):
    # Check if a's type comes later than b's alphabetically.
    # We will label our collision types in alphabetical order, 
    # so the lower one needs to go first.
    if a.contact_type == "Sprite3D":
        a = a.collide_shape
    if b.contact_type == "Sprite3D":
        b = b.collide_shape
    
    if b.contact_type < a.contact_type:
        a, b = b, a
    # This calls the class of the appropriate name based on the two contact types.
    return globals()[f"{a.contact_type}_{b.contact_type}"](a, b, **kwargs)
    

# Generic contact class, to be overridden by specific scenarios
class Contact():
    def __init__(self, a:PhysicsObject, b:PhysicsObject, resolve=False, **kwargs):
        self.a = a
        self.b = b
        self.kwargs = kwargs
        self.overlap = 0
        self.normal = Vector2(0,0)
        self.update() # the update() function is created in the derived classes
        if resolve:
            self.resolve(update=False)
    
    def update(self):
        pass

    def resolve(self, update=True, **kwargs):
        if update:
            self.update()
        
        # This pattern first checks keywords to resolve, then keywords given to contact.
        # Keywords given here to resolve override the previous ones given to contact.
        restitution = kwargs.get("restitution", self.kwargs.get("restitution", 0)) # 0 is default
        #friction = kwargs.get("friction", self.kwargs.get("friction", 0)) # 0 is default

        if self.overlap > 0:
            # RESOLVE OVERLAP
            m = 1/(1/self.a.mass + 1/self.b.mass) # reduced mass
            self.a.set(pos=self.a.pos + m/self.a.mass*self.overlap*self.normal)
            self.b.set(pos=self.b.pos - m/self.b.mass*self.overlap*self.normal)
            
            # RESOLVE VELOCITY
            point = self.point()
            sa = point - self.a.pos
            sb = point - self.b.pos
            va = self.a.vel + math.radians(self.a.avel)*sa.rotate(90)
            vb = self.b.vel + math.radians(self.b.avel)*sb.rotate(90)
            v = va - vb
            vdotn = v.dot(self.normal)
            if vdotn < 0: # only if they moving toward each other
                # Calculate new m for rotational collision
                m = 1/(1/m + sa.cross(self.normal)**2/self.a.momi 
                           + sb.cross(self.normal)**2/self.b.momi)
                Jn = -(1 + restitution) * m * vdotn

                # tangent = self.normal.rotate(90)
                # vdott = v.dot(tangent)
                # Jt = -m*vdott
                # # Check if this Jt is within limits
                # if abs(Jt) < friction*Jn:
                #     # Sticking friction, no need to change Jt
                #     pass
                #     shift_vector = vdott/vdotn * self.overlap * tangent
                #     self.a.pos += shift_vector * m/self.a.mass
                #     self.b.pos -= shift_vector * m/self.b.mass
                # else:
                #     # Sliding friction
                #     Jt = friction*Jn*math.copysign(1, -vdott)
                
                impulse = Jn * self.normal #+ Jt * tangent
                self.a.impulse(impulse, point)
                self.b.impulse(-impulse, point)

# def Sprite3D_Sprite3D(a:Sprite3D, b:Sprite3D, **kwargs):
#     if a.collide_shape is not None and b.collide_shape is not None:
#         return generate(a.collide_shape, b.collide_shape, **kwargs)
#     else:
#         return Contact(a, b)

# def Polygon_Sprite3D(a:Polygon, b:Sprite3D, **kwargs):
#     if b.collide_shape is not None:
#         return generate(a, b.collide_shape, **kwargs)
#     else:
#         return Contact(a, b)

# def Circle_Sprite3D(a:Circle, b:Sprite3D, **kwargs):
#     if b.collide_shape is not None:
#         return generate(a, b.collide_shape, **kwargs)
#     else:
#         return Contact(a, b)

# Contact class for two circles
class Circle_Circle(Contact):
    def update(self):  # compute the appropriate values
        self.a : Circle
        self.b : Circle
        r = self.a.pos - self.b.pos
        self.overlap = self.a.radius + self.b.radius - r.magnitude()
        self.normal = r.normalize()

    def point(self):
        return self.a.pos - self.a.radius*self.normal


# Contact class for Circle and a Wall
# Circle is before Wall because it comes before it in the alphabet
class Circle_Wall(Contact):
    def update(self):  # compute the appropriate values
        self.a : Circle
        self.b : Wall
        r = self.a.pos - self.b.pos
        factor = max(abs(self.b.normal.x), abs(self.b.normal.y))
        self.overlap = self.a.radius - r.dot(self.b.normal) + self.b.width/2*factor
        self.normal = self.b.normal

    def point(self):
        return self.a.pos - self.a.radius*self.normal


# Empty class for Wall - Wall collisions
# The intersection of two infinite walls is not interesting, so skip them
class Wall_Wall(Contact):
    pass

class Polygon_Wall(Contact):
    def update(self):
        self.a: Polygon
        self.b: Wall
        # Loop over all points on the polygon and find the most overlapped point
        self.overlap = -math.inf
        for i, point in enumerate(self.a.points):
            overlap = -(point - self.b.pos).dot(self.b.normal)
            if overlap > self.overlap:
                self.overlap = overlap
                self.index = i
        self.normal = self.b.normal
                
    def point(self):
        return self.a.points[self.index]

class Polygon_Polygon(Contact):
    def update(self):
        self.a: Polygon
        self.b: Polygon
        self.overlap = math.inf
        if self.update_half(self.a, self.b):
            self.update_half(self.b, self.a)
            if self.point_polygon is self.b:
                self.normal = -self.normal
        
    def update_half(self, a: Polygon, b: Polygon):
        for pos, normal in zip(b.points, b.normals):
            wall_overlap = -math.inf
            for i, point in enumerate(a.points):
                overlap = -(point - pos).dot(normal)
                if overlap > wall_overlap:
                    wall_overlap = overlap
                    wall_index = i
            if wall_overlap < self.overlap:
                self.overlap = wall_overlap
                self.normal = normal
                self.index = wall_index
                self.point_polygon = a
                if self.overlap < 0:
                    return False
        return True

    def point(self):
        return self.point_polygon.points[self.index]
        

class Circle_Polygon(Contact):
    def update(self):
        self.a : Circle
        self.b : Polygon
        # self.overlap needs to be the minimum overlap
        # First set it to infinity and then keep searching for lower values
        self.overlap = math.inf
        for i, (point, normal) in enumerate(zip(self.b.points, self.b.normals)):
            r = self.a.pos - point
            overlap = self.a.radius - r.dot(normal)
            if overlap < self.overlap:
                self.overlap = overlap
                self.normal = normal
                index = i
                if self.overlap <= 0:
                    break
        if 0 < self.overlap < self.a.radius:
            endpoint1 = self.b.points[index]
            endpoint2 = self.b.points[index-1]
            if (self.a.pos - endpoint1).dot(endpoint1 - endpoint2) > 0:
                r = self.a.pos - endpoint1
                self.overlap = self.a.radius - r.magnitude()
                self.normal = r.normalize()
            elif (self.a.pos - endpoint2).dot(endpoint2 - endpoint1) > 0:
                r = self.a.pos - endpoint2
                self.overlap = self.a.radius - r.magnitude()
                self.normal = r.normalize()

    def point(self):
        return self.a.pos - self.a.radius*self.normal
        
