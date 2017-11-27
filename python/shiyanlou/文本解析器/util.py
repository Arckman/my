def lines(file):
    """
    generator, add \n to last line
    """
    for line in file:yield line
    yield "\n"

def blocks(file):
    """
    generator, generate text block
    """
    block=[]
    for line in lines(file):
        if line.strip():
            block.append(line)
        elif block:
            yield ''.join(block).strip()
            block=[]
    