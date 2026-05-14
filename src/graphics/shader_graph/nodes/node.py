from src.graphics.shader_graph.vars.var import Var
import uuid

# ------------------------
# Node Segstem
# ------------------------

class Node(Var):
    def __init__(self, type, inputs=[]):
        super().__init__(type)

        self.inputs = inputs
        self.id = f"v_{uuid.uuid4().hex[:8]}"

    def emit(self):
        raise NotImplementedError()

    def emit_object(self):
        return self.id
    