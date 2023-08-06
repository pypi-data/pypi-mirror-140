from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A


class ManageEventsTable(tables.Table):
    class Meta:
        attrs = {"class": "responsive-table highlight"}

    display_name = tables.Column(verbose_name=_("Event"))
    date_event = tables.Column(verbose_name=_("Date"))
    max_participants = tables.Column(verbose_name=_("Max. participants"))
    date_registration = tables.Column(verbose_name=_("Registration until"))

    edit = tables.LinkColumn(
        "edit_event_by_slug",
        args=[A("slug")],
        verbose_name=_("Edit"),
        text=_("Edit"),
    )
    view = tables.LinkColumn(
        "event_by_name",
        args=[A("slug")],
        verbose_name=_("View"),
        text=_("View"),
    )


class VouchersTable(tables.Table):
    class Meta:
        attrs = {"class": "responsive-table highlight"}

    event = tables.Column(verbose_name=_("Event"))
    discount = tables.Column(verbose_name=_("Amount"))
    code = tables.Column(verbose_name=_("Code"))
    person = tables.Column(verbose_name=_("Person"))
    deleted = tables.LinkColumn(
        "delete_voucher_by_pk",
        args=[A("id")],
        verbose_name=_("Delete"),
        text=_("Delete"),
    )
    edit = tables.LinkColumn(
        "edit_voucher_by_pk", args=[A("id")], verbose_name=_("Edit"), text=_("Edit")
    )
    print_voucher = tables.LinkColumn(
        "print_voucher_by_pk", args=[A("id")], verbose_name=_("Print"), text=_("Print")
    )


class EventRegistrationsTable(tables.Table):
    class Meta:
        attrs = {"class": "responsive-table highlight"}

    person = tables.Column()
    event = tables.Column()
    date_registered = tables.Column()
    view = tables.LinkColumn(
        "registration_by_pk",
        args=[A("id")],
        verbose_name=_("View registration"),
        text=_("View"),
    )


class TermsTable(tables.Table):
    class Meta:
        attrs = {"class": "responsive-table highlight"}

    title = tables.Column()

    edit = tables.LinkColumn(
        "edit_term_by_pk",
        args=[A("id")],
        verbose_name=_("Edit"),
        text=_("Edit"),
    )


class InfoMailingsTable(tables.Table):
    class Meta:
        attrs = {"class": "responsive-table highlight"}

    subject = tables.Column()

    edit = tables.LinkColumn(
        "edit_info_mailing_by_pk",
        args=[A("id")],
        verbose_name=_("Edit"),
        text=_("Edit"),
    )
    delete = tables.LinkColumn(
        "delete_info_mailing_by_pk",
        args=[A("id")],
        verbose_name=_("Delete"),
        text=_("Delete"),
    )
