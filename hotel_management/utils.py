from datetime import date

LINE  = "─" * 65
DLINE = "═" * 65

def header(title):
    print(f"\n{DLINE}")
    print(f"  {'GRAND PALACE HOTEL':^45}")
    print(f"  {title:^45}")
    print(f"{DLINE}")

def subheader(title):
    print(f"\n{LINE}")
    print(f"  {title}")
    print(LINE)

def success(msg): print(f"\n  ✔  {msg}")
def error(msg):   print(f"\n  ✘  {msg}")
def info(msg):    print(f"\n  ℹ  {msg}")

def table(headers, rows, widths=None):
    if not rows:
        print("  (no records found)")
        return
    if not widths:
        widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) + 2
                  for i, h in enumerate(headers)]
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    sep = "  " + "  ".join("-" * w for w in widths)
    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        print(fmt.format(*[str(row[i]) if i < len(row) else "" for i in range(len(headers))]))

def print_bill(bill_data):
    print(f"\n{'═'*50}")
    print(f"{'GRAND PALACE HOTEL':^50}")
    print(f"{'TAX INVOICE':^50}")
    print(f"{'═'*50}")
    print(f"  Guest      : {bill_data['guest_name']}")
    print(f"  Phone      : {bill_data['phone']}")
    print(f"  Room       : {bill_data['room_number']} ({bill_data['room_type']})")
    print(f"  Check-in   : {bill_data['check_in']}")
    print(f"  Check-out  : {bill_data['check_out']}")
    print(f"  Nights     : {bill_data['nights']}")
    print(f"{'─'*50}")
    print(f"  Room Charges  : {bill_data['nights']} × ₹{bill_data['price_per_night']:.2f}"
          f" = ₹{bill_data['room_charges']:.2f}")
    print(f"  Restaurant    : ₹{bill_data['rest_charges']:.2f}")
    print(f"  GST (12%)     : ₹{bill_data['tax_amount']:.2f}")
    print(f"{'─'*50}")
    print(f"  TOTAL         : ₹{bill_data['total']:.2f}")
    print(f"{'═'*50}")

def pause():
    input("\n  Press Enter to continue...")

def prompt(msg, default=None):
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"  {msg}{suffix}: ").strip()
    return val if val else (str(default) if default is not None else "")

def choose(msg, choices):
    while True:
        val = input(f"  {msg} ({'/'.join(choices)}): ").strip().upper()
        if val in [c.upper() for c in choices]:
            return val
        print("  Invalid choice.")

def get_int(msg, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(f"  {msg}: ").strip())
            if min_val is not None and val < min_val:
                print(f"  Minimum value is {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  Maximum value is {max_val}.")
                continue
            return val
        except ValueError:
            print("  Please enter a valid number.")

def get_date(msg):
    while True:
        val = input(f"  {msg} (YYYY-MM-DD): ").strip()
        try:
            date.fromisoformat(val)
            return val
        except ValueError:
            print("  Invalid date. Use YYYY-MM-DD format.")

def get_float(msg):
    while True:
        try:
            return float(input(f"  {msg}: ").strip())
        except ValueError:
            print("  Please enter a valid number.")
