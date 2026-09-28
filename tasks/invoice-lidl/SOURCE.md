# Source

This task uses image `20210429_200847.jpg` from [Francisco Cruz's InvoicesReceiptsPT dataset](https://huggingface.co/datasets/Francisco-Cruz/InvoicesReceiptsPT), revision `a3f7a8ad4b8cfd37495293153f14e22d072327ea`. [Open this exact image](https://huggingface.co/datasets/Francisco-Cruz/InvoicesReceiptsPT/blob/a3f7a8ad4b8cfd37495293153f14e22d072327ea/1_Images/20210429_200847.jpg) and its [published annotation](https://huggingface.co/datasets/Francisco-Cruz/InvoicesReceiptsPT/blob/a3f7a8ad4b8cfd37495293153f14e22d072327ea/2_Annotations_Json/20210429_200847.txt).

The source collection contains real Portuguese invoices and receipts. The image is unchanged; `tests/expected.json` maps the published fields to the demo schema, normalizes dates and amounts, and adds a short human-written purchase summary. The original dataset is also [archived on Zenodo](https://zenodo.org/records/6371710) under CC BY 4.0. This repo adds task instructions, a rubric, and the reference mapping.
