from typing import List, Dict

def calculate_invoice_totals(items: List[Dict[str, float]], tax_rate: float = 0.0, discount_amount: float = 0.0) -> Dict[str, float]:
    subtotal = 0.0
    for item in items:
        line_total = item['quantity'] * item['unit_price']
        subtotal += line_total

    tax_total = (subtotal - discount_amount) * (tax_rate / 100.0) if tax_rate > 0 else 0.0
    grand_total = max(0.0, (subtotal - discount_amount) + tax_total)

    return {
        "subtotal": round(subtotal, 2),
        "tax_total": round(tax_total, 2),
        "discount_total": round(discount_amount, 2),
        "grand_total": round(grand_total, 2)
    }
