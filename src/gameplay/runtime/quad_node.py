from gameplay.physics.aabb import AABB

class QuadNode:
        MAX_OBJECTS = 4
        MAX_DEPTH = 6

        def __init__(
                self,
                bounds: AABB,
                depth: int = 0
        ):

                self.bounds = bounds
                self.depth = depth

                self.entities: list[tuple[str, AABB]] = []

                self.children: list[QuadNode] | None = None

        def subdivide(self):
                x = self.bounds.x
                y = self.bounds.y

                w = self.bounds.width / 2
                h = self.bounds.height / 2

                self.children = [
                        # NW
                        QuadNode(
                                AABB(x, y, w, h),
                                self.depth + 1
                        ),
                        # NE
                        QuadNode(
                                AABB(x + w, y, w, h),
                                self.depth + 1
                        ),
                        # SW
                        QuadNode(
                                AABB(x, y + h, w, h),
                                self.depth + 1
                        ),
                        # SE
                        QuadNode(
                                AABB(x + w, y + h, w, h),
                                self.depth + 1
                        )
                ]
        
        def get_child_for(
                self,
                aabb: AABB
        ):
                if self.children is None:
                        return None

                for child in self.children:
                        if child.bounds.contains(aabb):
                                return child

                return None
        
        def insert(
                self,
                entity_id: str,
                aabb: AABB
        ):
                # try descending first
                if self.children is not None:
                        child = self.get_child_for(aabb)

                        if child is not None:
                                child.insert(entity_id, aabb)
                                return

                # otherwise store locally
                self.entities.append(
                        (entity_id, aabb)
                )

                # subdivide if needed
                if len(self.entities) > self.MAX_OBJECTS and self.depth < self.MAX_DEPTH:
                        if self.children is None:
                                self.subdivide()

                        # redistribute
                        i = 0

                        while i < len(self.entities):
                                entity, entity_aabb = self.entities[i]
                                child = self.get_child_for(entity_aabb)

                                if child is not None:
                                        child.insert(
                                                entity,
                                                entity_aabb
                                        )
                                        self.entities.pop(i)
                                else:
                                        i += 1
        
        def query(
                self,
                area: AABB,
                found = None
        ):

                if found is None:
                        found = []

                # prune entire node
                if not self.bounds.intersects(area):
                        return found

                # test local entities
                for entity_id, aabb in self.entities:
                        if aabb.intersects(area):
                                found.append(entity_id)

                # recurse
                if self.children is not None:
                        for child in self.children:
                                child.query(area, found)

                return found