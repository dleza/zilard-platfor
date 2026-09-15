from django import template
from django.utils.html import format_html, format_html_join

register = template.Library()


@register.simple_tag
def render_field(field):
    errors = format_html_join(
        "",
        '<p class="mt-1 text-sm font-medium text-red-700">{}</p>',
        ((error,) for error in field.errors),
    )
    help_text = ""
    if field.help_text:
        help_text = format_html('<p class="mt-1 text-xs text-slate-600">{}</p>', field.help_text)

    if getattr(field.field.widget, "input_type", "") == "checkbox":
        return format_html(
            '<div class="field-group"><label class="flex items-start gap-3 text-sm font-medium text-slate-800" for="{}">{}<span>{}</span></label>{}{}</div>',
            field.id_for_label,
            field,
            field.label,
            help_text,
            errors,
        )

    return format_html(
        '<div class="field-group"><label class="field-label" for="{}">{}</label>{}{}{}</div>',
        field.id_for_label,
        field.label,
        field,
        help_text,
        errors,
    )
