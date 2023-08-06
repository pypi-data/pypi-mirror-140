_trace = []
_varsToStore = []
_started = False
_print = print
_input = input
_ios = []


def print(*values, sep=' ', end='\n', file=None, flush=False):
    if _started:
        _ios.append((len(_trace), "o", (sep.join([str(v) for v in values]) + end).replace('\n', '')))
    _print(*values, sep=sep, end=end, file=file, flush=flush)


def input(*__prompt):
    val = _input(*__prompt)
    if _started:
        _ios.append((len(_trace), "i", val))
    return val


def initialize(*varNames):
    global _varsToStore, _started
    _varsToStore = varNames
    _started = True


def trace(line, vars):
    _trace.append((line, {var: vars[var] if var in vars else None for var in _varsToStore}))


def display():
    global _started
    oldStarted = _started
    _started = False
    columnWidths = [max(5, *[len(str(var)) for var in _varsToStore])] + [max(len(str(i)), len(str(t[0])), *[len(str(t[1][var])) for var in _varsToStore]) for i, t in enumerate(_trace)]
    totalWidth = sum(columnWidths) + 3 * (len(columnWidths) - 1)
    print(" | ".join(["Etape" + " " * (columnWidths[0] - 5)] + [str(i) + " " * (columnWidths[i+1] - len(str(i))) for i in range(len(_trace))]))
    print("-" * totalWidth)
    # simple stuff to print a tab. trivial
    print(" | ".join(["Ligne" + " " * (columnWidths[0] - 5)] + [str(t[0]) + " " * (width - len(str(t[0]))) for t, width in zip(_trace, columnWidths[1:])]))
    print("-" * totalWidth)
    print(("\n" + "-" * totalWidth + "\n").join([" | ".join([var + " " * (columnWidths[0] - len(var))] + [str(_trace[i][1][var]) + " " * (columnWidths[i + 1] - len(str(_trace[i][1][var]))) for i in range(len(_trace))]) for var in _varsToStore]))
    [print("Etape " + str(io[0]) + " : " + ("Affichage" if io[1] == "o" else "Entrée") + " de '" + io[2] + "'") for io in _ios]
    _started = oldStarted


def stop():
    global _started
    _started = False


def reset():
    global _started
    _trace.clear()
    _varsToStore.clear()
    _ios.clear()
    _started = False


__all__ = ["print", "input", "initialize", "trace", "display", "stop", "reset"]
