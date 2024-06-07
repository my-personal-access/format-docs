"""YAML dumper module."""
from yaml import SafeDumper


class LotDumper(SafeDumper):
    """Prettify yaml writing in files."""
    
    def write_line_break(self, data=None):
        """HACK: insert blank lines between top-level objects inspired by https://stackoverflow.com/a/44284819/3786245."""
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()

    def increase_indent(self, flow=False, indentless=False):
        """Dumper indent."""
        return super().increase_indent(flow, False) # LotDumper, self
