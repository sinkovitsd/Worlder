from pygame.math import Vector2, Vector3
import pygame
import math

class PhysicsObject3D:
    def __init__(self, pos=(0,0,0), vel=(0,0,0), mass=1, collide_shape=None, visible=True):
        self.pos = Vector3(pos)
        self.vel = Vector3(vel)
        self.mass = mass
        self.force = Vector3(0,0,0) 
        self.visible = visible
        self.collide_shape = collide_shape 
        if self.collide_shape is not None:
            self.collide_shape.set(pos = Vector2(self.pos.x, self.pos.y))
            self.collide_shape.mass = self.mass  
            self.collide_shape.owner = self
        self.contact_type = "Sprite3D"   
               
    def clear_force(self):
        self.force *= 0

    def add_force(self, force):
        self.force += force

    def impulse(self, impulse):
        self.vel += impulse/self.mass

    def set(self, pos=None):
        if pos is not None:
            self.pos = Vector3(pos)
            if self.collide_shape is not None:
                self.collide_shape.set(pos = Vector2(self.pos.x, self.pos.y))

    def update(self, dt):
        # update velocity using the current force
        self.vel += self.force/self.mass * dt
        # update position using the newly updated velocity
        self.pos += self.vel * dt
        if self.collide_shape is not None:
            self.collide_shape.set(pos=self.pos)
        
class Sprite3D(PhysicsObject3D):
    def __init__(self, image=None, origin=(0,0), **kwargs):
        self.image = image
        self.origin = Vector2(origin)
        super().__init__(**kwargs)

    def draw(self, window, horizon, yfactor):
        # if self.collide_shape is not None:
        #     self.collide_shape.draw(window)
        if self.visible:
            pos = Vector2(self.pos.x, horizon + self.pos.y*yfactor - self.pos.z)
            window.blit(self.image, pos - self.origin)

class PhysicsObject:
    def __init__(self, pos=(0,0), vel=(0,0), mass=1, angle=0, avel=0, momi=math.inf, owner=None, visible=False):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.angle = angle
        self.avel = avel
        self.momi = momi
        self.owner = owner
        self.visible = visible
        self.old_pos = Vector2(self.pos)
        self.force = Vector2(0,0)       

    def clear_force(self):
        self.force *= 0

    def add_force(self, force):
        self.force += force

    def impulse(self, impulse, point=None):
        self.vel += impulse/self.mass
        if point is not None:
            s = point - self.pos
            self.avel += math.degrees(s.cross(impulse)/self.momi)
        if self.owner is not None:
            self.owner.vel = Vector3(self.vel.x, self.vel.y, self.owner.vel.z)
            
    def set(self, pos=None, angle=None):
        if pos is not None:
            self.pos = Vector2(pos[0:2])
            if self.owner is not None:
                self.owner.pos = Vector3(self.pos.x, self.pos.y, self.owner.pos.z)
        if angle is not None:
            self.angle = angle
            
    def update(self, dt):
        if self.owner is not None:
            self.owner.update(dt)
        else:
            # update velocity using the current force
            self.vel += self.force/self.mass * dt
            # update position using the newly updated velocity
            self.pos += self.vel * dt
            self.angle += self.avel * dt
        

class Circle(PhysicsObject):
    def __init__(self, radius=100, color=(255,255,255), width=0, **kwargs):
        # kwargs = keyword arguments
        self.color = Vector3(color)
        self.radius = radius
        self.width = width
        super().__init__(**kwargs)
        self.contact_type = "Circle"

    def draw(self, window, color=None, width=None):
        if self.visible:
            if color is None:
                color = self.color
            if width is None:
                width = self.width
            pygame.draw.circle(window, color, self.pos, self.radius, width)

class Wall(PhysicsObject):
    def __init__(self, start=(0,0), end=(0,0), color=(255,255,255), width=1):
        self.point1 = Vector2(start)
        self.point2 = Vector2(end)
        self.color = color
        self.width = width
        self.normal = (self.point2 - self.point1).normalize().rotate(90)
        super().__init__(pos=(self.point1 + self.point2)/2, mass=math.inf)
        self.contact_type = "Wall"


    def draw(self, window):
        if self.visible:
            pygame.draw.line(window, self.color, self.point1, self.point2, self.width)
            #pygame.draw.line(window, self.color, self.pos, self.pos + 100*self.normal)

class Polygon(PhysicsObject):
    def __init__(self, local_points=[], color=[255,255,255], width=0, normals_length=100, **kwargs):
        self.local_points = [Vector2(x) for x in local_points]
        self.local_normals = [(self.local_points[i] - self.local_points[i-1]).normalize().rotate(90) 
                              for i in range(len(self.local_points))]
        
        # Check for flipped normals or nonconvex polygons
        for point, normal in zip(self.local_points, self.local_normals):
            d = [(p - point).dot(normal) for p in self.local_points]
            pos = sum(x > 1e-12 for x in d)
            neg = sum(x < -1e-12 for x in d)
            if pos > 0:
                if neg == 0:
                    normal *= -1 # flip the normal around
                else:
                    raise(ValueError, "Nonconvex polygon defined.")
               
        self.color = color
        self.width = width
        self.normals_length = normals_length
        super().__init__(**kwargs)
        self.update_polygon()
        self.contact_type = "Polygon"

    def update_polygon(self):
        self.points = [local_point.rotate(self.angle) + self.pos for local_point in self.local_points]
        self.normals = [local_normal.rotate(self.angle) for local_normal in self.local_normals]
        # self.points = []
        # for local_point in self.local_points:
        #     self.points.append(local_point.rotate(self.angle) + self.pos)

    def update(self, dt):
        super().update(dt)
        self.update_polygon()

    def set(self, pos=None, angle=None):
        super().set(pos=pos, angle=angle)
        self.update_polygon()
    
    def draw(self, window):
        if self.visible:
            pygame.draw.polygon(window, self.color, self.points, self.width)
            if self.normals_length > 0:
                for point, normal in zip(self.points, self.normals):
                    pygame.draw.line(window, [0,0,0], point, point + self.normals_length*normal)


class UniformCircle(Circle):
    def __init__(self, density=1, radius=100, **kwargs):
        # calculate mass and moment of inertia
        mass = density * math.pi * radius**2
        momi = 0.5 * mass * radius**2
        super().__init__(mass=mass, momi=momi, radius=radius, **kwargs)


class UniformPolygon(Polygon):
    def __init__(self, mass=None, density=None, local_points=[], pos=[0,0], angle=0, shift=True, **kwargs):
        if mass is not None and density is not None:
            raise("Cannot specify both mass and density.")
        if mass is None and density is None:
            mass = 1 # if nothing specified, default to mass = 1
        
        # Calculate mass, moment of inertia, and center of mass
        # by looping over all "triangles" of the polygon
        # assume a density of 1, scale later
        total_mass = 0
        total_momi = 0
        com_numerator = Vector2(0,0)
        for i in range(len(local_points)):
            s0 = Vector2(local_points[i])
            s1 = Vector2(local_points[i-1])
            # triangle mass
            triangle_mass = 1 * 0.5 * s0.cross(s1)
            # triangle moment of inertia
            triangle_momi = triangle_mass/6 * (s0*s0 + s1*s1 + s0*s1)
            # triangle center of mass
            triangle_com = (s0 + s1)/3

            # add to total mass
            total_mass += triangle_mass
            # add to total moment of inertia
            total_momi += triangle_momi
            # add to center of mass numerator
            com_numerator += triangle_mass * triangle_com
        
        # calculate total center of mass by dividing numerator by denominator (total mass)
        com = com_numerator / total_mass

        # if total_mass is negative, flip mass and momi
        if total_mass < 0:
            total_mass *= -1
            total_momi *= -1

        # if mass is specified, then scale mass and momi
        if mass is not None:
            total_momi *= mass/total_mass
            total_mass = mass
        # if density is specified, then scale mass and momi
        if density is not None:
            total_momi *= density
            total_mass *= density

        # Usually we shift local_points origin to center of mass
        if shift:
            # Shift local_points by com
            new_local_points = []
            for p in local_points:
                new_local_points.append(Vector2(p) - com)
            # shift pos
            pos = pos + com.rotate(angle)
            # Use parallel axis theorem to correct the moment of inertia
            total_momi -= total_mass*com.magnitude_squared()
        else:
            new_local_points = local_points
        
        # Then call super().__init__() with those correct values
        super().__init__(mass=total_mass, momi=total_momi, local_points=new_local_points, pos=pos, angle=angle, **kwargs) 

    # def draw(self, window):
    #     super().draw(window)
    #     pygame.draw.circle(window, (255,255,255), self.pos, 5) # draw center of mass, to test

# shape = UniformPolygon(density=0.01, local_points=[[0,0],[20,0],[20,10],[0,10]])
# print(shape.mass, 0.01*10*20)  # check mass
# print(shape.momi, shape.mass/12*(10**2+20**2))  # check moment of inertia
# print(shape.local_points)  # check if rectangle is centered (checks center of mass)
