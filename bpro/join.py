from pro import right, left, top, bottom
from pro import context
from .shape import createRectangle

class JoinManager:
    def __init__(self):
        # store end1 of alls band in self.ends1 dictionary
        self.ends1 = {}
        # store end2 of alls band in self.ends2 dictionary
        self.ends2 = {}
        # closed bands
        self.closed = []
        # dictionary of tuples (shape, instance_of_join_operator), shape.face.index is used as a key
        self.shapes = {}
    
    def process(self, deferred):
        # TODO: process firstLoop correctly if join.neighbor==top or join.neighbor==bottom
        shape = deferred[0]
        join = deferred[1]
        operator = join.operator
        
        ends1 = self.ends1
        ends2 = self.ends2
        firstLoop = shape.firstLoop
        nghbr = join.neighbor
        if nghbr==right:
            neighbor = firstLoop.link_loop_next
        elif nghbr==left:
            neighbor = firstLoop.link_loop_prev
        elif nghbr==top:
            neighbor = firstLoop.link_loop_next.link_loop_next
        elif nghbr==bottom:
            neighbor = firstLoop
        neighbor = neighbor.link_loops[0].face.index
        face = shape.face.index
        # store deferred in self.shapes
        self.shapes[face] = deferred
        
        if face in ends1:
            band = ends1[face]
            if nghbr==left or nghbr==bottom:
                if neighbor == band.end2:
                    # got a closed band
                    self.closeBand(band)
                elif neighbor in ends2:
                    # merge two bands
                    self.merge(ends2[neighbor], band)
                else:
                    self.extendLeft(band, neighbor, operator)
            elif not band.operator and operator:
                # If nghbr==right or nghbr==top: this case means two rectangles pointing to each other.
                # Perform here operator check only
                band.operator = operator
        elif face in ends2:
            band = ends2[face]   
            if nghbr==right or nghbr==top:
                if neighbor == band.end1:
                    # got a closed band
                    self.closeBand(band)
                elif neighbor in ends1:
                    # merge two bands
                    self.merge(band, ends2[neighbor])
                else:
                    self.extendRight(band, neighbor, operator)
            elif not band.operator and operator:
                # If nghbr==left or nghbr==bottom: this case means two rectangles pointing to each other.
                # Perform here operator check only
                band.operator = operator
        elif neighbor in ends1:
            self.extendLeft(ends1[neighbor], face, operator)
        elif neighbor in ends2:
            self.extendRight(ends2[neighbor], face, operator)
        else:
            # start a new band
            if nghbr == right or nghbr==top:
                end1 = face
                end2 = neighbor
            elif nghbr == left or nghbr==bottom:
                end1 = neighbor
                end2 = face
                firstLoop = firstLoop.link_loop_prev.link_loops[0].link_loop_prev
            band = Band(end1, end2, firstLoop, operator)
            band.shapes = self.shapes
            ends1[end1] = band
            ends2[end2] = band
    
    def closeBand(self, band):
        del self.ends1[band.end1]
        del self.ends2[band.end2]
        band.closed = True
        self.closed.append(band)
    
    def merge(self, band1, band2):
        """
        Merge band1 and band2.
        
        Only band1 goes further. band2 will be forgotten.
        """ 
        ends2 = self.ends2
        del ends2[band1.end2]
        del self.ends1[band2.end1]
        ends2[band2.end2] = band1
        band1.end2 = band2.end2
        if not band1.operator and band2.operator:
            band1.operator = band2.operator
    
    def extendLeft(self, band, index, operator):
        ends1 = self.ends1
        del ends1[band.end1]
        ends1[index] = band
        band.end1 = index
        if operator and not band.operator:
            band.operator = operator
        # update also firstLoop of band
        band.firstLoop = band.firstLoop.link_loop_prev.link_loops[0].link_loop_prev
    
    def extendRight(self, band, index, operator):
        ends2 = self.ends2
        del ends2[band.end2]
        ends2[index] = band
        band.end2 = index
        if operator and not band.operator:
            band.operator = operator
    
    def finalize(self):
        # process closed bands of rectangle
        for band in self.closed:
            band.operator.execute_join(band)
        # process band of rectangle with open ends
        ends = self.ends1
        for index in ends:
            band = ends[index]
            operator = band.operator
            if operator:
                operator.execute_join(band)


class Band:
    def __init__(self, end1, end2, firstLoop, operator):
        # check if need to set operator
        self.operator = operator if operator else None
        self.closed = False
        # index of the starting face
        self.end1 = end1
        # index of the finishing end
        self.end2 = end2
        # the first loop of self.end1
        self.firstLoop = firstLoop
    
    def extrude(self):
        print("processing loop:", self.end1, self.end2)
        bm = context.bm
        depth = self.operator.depth
        # inset or offset?
        inset = True if depth>0 else False
        
        loop = self.firstLoop
        normal = depth * loop.face.normal
        # lower vertex (along the first loop)
        vert1 = loop.vert.co
        # neighbor of vert1 to the right
        vert = loop.link_loop_next.vert.co
        # vector from vert1 to vert
        vec1 = vert - vert1
        vec1.normalize()
        # vector along the height of the band of rectangles
        axis = loop.link_loop_prev.vert.co - vert1
        if self.closed:
            # the special case of a closed band of rectangles
            # previous loop
            _loop = loop.link_loop_prev.link_loops[0].link_loop_prev
            vec2 = _loop.vert.co - vert1
            vec2.normalize()
            # cosine and sine of the angle between vec2 and vec1
            cos = vec2.dot(vec1)
            sin = vec2.cross(vec1).length
            _vertEx1 = vert1 + normal - (depth+depth*cos)/sin*vec1
            _vertEx2 = bm.verts.new(_vertEx1 + axis)
            _vertEx1 = bm.verts.new(_vertEx1)
            prevVertEx1 = _vertEx1
            prevVertEx2 = _vertEx2
        else:
            # extruded counterpart of vert1
            prevVertEx1 = vert1 + normal
            # upper vertex (upper neighbor of vert1)
            prevVertEx2 = bm.verts.new(prevVertEx1 + axis)
            prevVertEx1 = bm.verts.new(prevVertEx1)
            # starting rectangle
            createRectangle((loop.vert, prevVertEx1, prevVertEx2, loop.link_loop_prev.vert))

        index = self.end1
        while True:
            context.facesForRemoval.append(loop.face)
            _loop = loop
            _loopNext = _loop.link_loop_next
            if index==self.end2:
                break
            # next loop
            loop = loop.link_loop_next.link_loops[0].link_loop_next
            # neighbor of vert to the right
            vert2 = loop.link_loop_next.vert.co
            # vector from vert to vert2
            vec2 = vert2 - vert
            vec2.normalize()
            # cosine and sine of the angle between -vec1 and vec2
            cos = -(vec1.dot(vec2))
            sin = vec1.cross(vec2).length
            # extruded counterpart of vert
            vertEx1 = vert + normal + (depth+depth*cos)/sin*vec1
            vertEx2 = bm.verts.new(vertEx1 + axis)
            vertEx1 = bm.verts.new(vertEx1)
            createRectangle((prevVertEx1, vertEx1, vertEx2, prevVertEx2))
            # lower cap
            createRectangle((_loop.vert, _loopNext.vert, vertEx1, prevVertEx1))
            # upper cap
            createRectangle((_loopNext.link_loop_next.vert, _loop.link_loop_prev.vert, prevVertEx2, vertEx2))
            
            vec1 = vec2
            vert = vert2
            prevVertEx1 = vertEx1
            prevVertEx2 = vertEx2
            normal = depth * loop.face.normal
            
            index = loop.face.index
        
        if self.closed:
            vertEx1 = _vertEx1
            vertEx2 = _vertEx2
        else:
            vertEx1 = vert + normal
            vertEx2 = bm.verts.new(vertEx1 + axis)
            vertEx1 = bm.verts.new(vertEx1)
            # closing rectangle
            loop = loop.link_loop_next
            createRectangle((vertEx1, loop.vert, loop.link_loop_next.vert, vertEx2))
        createRectangle((prevVertEx1, vertEx1, vertEx2, prevVertEx2))
        # lower cap
        createRectangle((_loop.vert, _loopNext.vert, vertEx1, prevVertEx1))
        # upper cap
        createRectangle((_loopNext.link_loop_next.vert, _loop.link_loop_prev.vert, prevVertEx2, vertEx2))