class GCode:
    def __init__(self, dxf_entities) -> None:
        self.dxf_entities = dxf_entities
        self.instructions = []

    def prepare_instructions(self):
        self.instructions.append("G21 (Units in millimeters)")
        self.instructions.append("G90 (Absolute programming)")
        self.instructions.append("G17 (XY plane)")
        self.instructions.append("G40 (Cancel radius comp)")
        self.instructions.append("G0 Z15.000 (z safe margin)")

    def end_instructions(self):
        self.instructions.append("M2 (Program end)")

    def draw_circle(self):
        pass

    def move_xy(self, x, y):
        self.instructions.append(f"G01 X{x} Y{y}")

    def move_z(self, z):
        self.instructions.append(f"G01 Z{z}")

    def fast_move_xy(self, x, y):
        self.instructions.append(f"G00 X{x} Y{y}")

    def fast_move_z(self, z):
        self.instructions.append(f"G00 Z{z}")

    def generate(self) -> str:
        self.prepare_instructions()
        self.draw_circle()

        self.fast_move_z(15)
        self.end_instructions()
        print("\n".join(self.instructions))

        return "\n".join(self.instructions)
