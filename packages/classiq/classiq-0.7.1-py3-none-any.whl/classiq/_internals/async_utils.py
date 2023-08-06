def enable_jupyter_notebook() -> None:
    import nest_asyncio  # type: ignore[import]

    nest_asyncio.apply()


# =======================================================================
# According to stackoverflow.com's license
# taken from:
#   https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
# from the user:
#   https://stackoverflow.com/users/2132753/gustavo-bezerra
def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined]
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


# =======================================================================
