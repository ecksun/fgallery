class Config:
    args = None

    def __init__(self, args):
        self.args = args

    @property
    def input_folder(self):
        return self.args.input

    @property
    def output_folder(self):
        return self.args.output
