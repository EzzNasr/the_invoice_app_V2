import sys
import os
from Logic import functions
# ── Import resolution ─────────────────────────────────────────────────────────
# main.py lives in  .../the_invoice_app_V2/main/
# functions.py lives in  .../the_invoice_app_V2/Logic/
# Add Logic/ to sys.path so `import functions` resolves correctly
# regardless of which directory the user launches Python from.
# ─────────────────────────────────────────────────────────────────────────────
_MAIN_DIR     = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MAIN_DIR)
_LOGIC_DIR    = os.path.join(_PROJECT_ROOT, "Logic")

if _LOGIC_DIR not in sys.path:
    sys.path.insert(0, _LOGIC_DIR)


# =========================================================================
# main.py — Entry point for The Invoice App V2
#
# All logic lives in Logic/functions.py.
# main.py is intentionally thin: its only job is to call bill_type(),
# which runs the correct pipeline (Mock / Actual / Returned) based on
# the user's choice.
#
# Run from ANY directory:
#   python  the_invoice_app_V2/main/main.py
#   cd the_invoice_app_V2/main && python main.py
# Both work because paths inside functions.py are anchored to __file__,
# not to the working directory.
# =========================================================================

def main():
    functions.bill_type()

if __name__ == "__main__":
    main()
