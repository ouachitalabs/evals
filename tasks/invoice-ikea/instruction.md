# Extract one invoice from its image

Read the attached Portuguese invoice or receipt image. Return only a JSON object
with these seven string fields:

```json
{
  "seller_name": "seller's trading name, not the buyer",
  "seller_tax_id": "seller's nine-digit NIF or NIPC",
  "invoice_date": "YYYY-MM-DD",
  "invoice_number": "complete printed document reference, including its prefix",
  "total": "0.00",
  "tax_amount": "0.00",
  "order_summary": "One or two sentences describing what was purchased."
}
```

Use a dot and exactly two decimal places for euro amounts. Use `"0.00"` if
VAT is zero. Copy the final total rather than a unit price or cash tendered.
Describe visible items or services in the summary without inventing details.
The example above is fenced for readability only: reply with the bare JSON
object itself, with no code fences, no markdown, and nothing before or after it.
