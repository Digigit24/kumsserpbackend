from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False


def generate_document_number(prefix, model_class, field_name='created_at'):
    """Generate sequential number PREFIX-YYYY-NNNNN with yearly reset."""
    now = timezone.now()
    year = now.year
    with transaction.atomic():
        filter_kwargs = {}
        if hasattr(model_class, field_name):
            filter_kwargs[f"{field_name}__year"] = year
        last_record = model_class.objects.filter(**filter_kwargs).order_by('-id').first()
        last_seq = 0
        if last_record:
            for attr in [
                'requirement_number', 'quotation_number', 'po_number', 'grn_number',
                'indent_number', 'min_number', 'transaction_number', 'supplier_code'
            ]:
                existing = getattr(last_record, attr, None)
                if existing and str(existing).startswith(f"{prefix}-{year}-"):
                    try:
                        last_seq = int(str(existing).split('-')[-1])
                    except Exception:
                        last_seq = 0
                    break
        next_seq = last_seq + 1
        return f"{prefix}-{year}-{next_seq:05d}"


def _render_pdf(template_path, context):
    if not WEASYPRINT_AVAILABLE:
        return None
    html_string = render_to_string(template_path, context)
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer)
    return pdf_buffer.getvalue()


def _save_pdf(field, filename, pdf_bytes):
    if not (pdf_bytes and isinstance(field, object)):
        return
    field.save(filename, ContentFile(pdf_bytes), save=True)


def generate_po_pdf(purchase_order):
    pdf_bytes = _render_pdf('store/pdf/purchase_order.html', {'po': purchase_order})
    if hasattr(purchase_order, 'po_document') and purchase_order.po_number:
        _save_pdf(purchase_order.po_document, f"{purchase_order.po_number}.pdf", pdf_bytes)
    return pdf_bytes


def generate_min_pdf(material_issue_note):
    pdf_bytes = _render_pdf('store/pdf/material_issue_note.html', {'min': material_issue_note})
    if hasattr(material_issue_note, 'min_document') and material_issue_note.min_number:
        _save_pdf(material_issue_note.min_document, f"{material_issue_note.min_number}.pdf", pdf_bytes)
    return pdf_bytes


def generate_grn_pdf(goods_receipt_note):
    pdf_bytes = _render_pdf('store/pdf/goods_receipt_note.html', {'grn': goods_receipt_note})
    if hasattr(goods_receipt_note, 'invoice_file') and goods_receipt_note.grn_number:
        _save_pdf(goods_receipt_note.invoice_file, f"{goods_receipt_note.grn_number}.pdf", pdf_bytes)
    return pdf_bytes
