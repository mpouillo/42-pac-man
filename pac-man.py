import sys

# if running as PyInstaller executable
if hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False):
    from src.__main__ import main

    if __name__ == "__main__":
        main()

else:
    import runpy

    if __name__ == "__main__":
        runpy.run_module("src", run_name="__main__")
