def remove_preserve_tail(element):
    try:
        parent = element.getparent()
        if element.tail:
            prev = element.getprevious()
            if prev is not None:
                prev.tail = (prev.tail or '') + element.tail
            else:
                parent.text = (parent.text or '') + element.tail
        parent.remove(element)
    except AttributeError:
        return
