"""Read program argument(s)."""

def read(args):
    """Read program entries."""
    if len(args) < 2: raise Exception("Please pass project name to Python program.")
    
    return args[1]