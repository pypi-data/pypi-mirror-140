from datetime import datetime

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField
from django_iban.fields import IBANField

from aleksis.core.mixins import ExtensibleModel
from aleksis.core.models import Group, Person
from aleksis.core.util.core_helpers import generate_random_code, get_site_preferences
from aleksis.core.util.email import send_email


class Terms(ExtensibleModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    term = RichTextField(verbose_name=_("Term"))
    confirmation_text = models.TextField(verbose_name=_("Confirmation text"))

    def __str__(self) -> str:
        return self.title


class InfoMailing(ExtensibleModel):
    subject = models.CharField(max_length=255, verbose_name=_("subject"))
    text = RichTextField(verbose_name=_("Text"))
    reply_to = models.EmailField(verbose_name=_("Request replies to"), blank=True)

    active = models.BooleanField(verbose_name=_("Mailing is active"), default=False)

    sender = models.EmailField(verbose_name=_("Sender"), blank=True)
    send_to_person = models.BooleanField(verbose_name=_("Send to registered person"), default=True)
    send_to_guardians = models.BooleanField(verbose_name=_("Send to guardians"), default=False)

    sent_to = models.ManyToManyField(
        Person,
        verbose_name=_("Sent to persons"),
        related_name="received_info_mailings",
        editable=False,
        blank=True,
    )

    def __str__(self) -> str:
        return self.subject

    @classmethod
    def get_active_mailings(cls):
        return cls.objects.filter(active=True)

    def send(self):
        sent_to = self.sent_to.all()

        for event in self.events.all():
            for registration in event.registrations.all():
                if registration.person in sent_to:
                    continue

                subject = self.subject.format(
                    event=event, registration=registration, person=registration.person
                )
                body = self.text.format(
                    event=event, registration=registration, person=registration.person
                )

                if self.send_to_person:
                    to = [registration.person.email]
                    if self.send_to_guardians:
                        cc = registration.person.guardians.values_list("email", flat=True).all()
                    else:
                        cc = []
                elif self.send_to_guardians:
                    to = registration.person.guardians.values_list("email", flat=True).all()
                    cc = []

                sender = self.sender or get_site_preferences()["mail__address"]
                reply_to = self.reply_to or sender

                context = {"subject": subject, "body": body}
                send_email(
                    template_name="info_mailing",
                    context=context,
                    from_email=sender,
                    recipient_list=to,
                    cc=cc,
                    headers={
                        "Reply-To": reply_to,
                    },
                )

                self.sent_to.add(registration.person)


class Event(ExtensibleModel):
    # Event details
    display_name = models.CharField(verbose_name=_("Display name"), max_length=255)
    linked_group = models.OneToOneField(
        Group, on_delete=models.CASCADE, verbose_name=_("Group"), related_name="linked_event"
    )
    description = models.CharField(max_length=500, verbose_name=_("Description"))
    published = models.BooleanField(default=False, verbose_name=_("Publish"))
    place = models.CharField(max_length=50, verbose_name="Place")
    slug = models.SlugField(max_length=255, verbose_name=_("Slug"), blank=True)

    # Date details
    date_event = models.DateField(verbose_name=_("Date of event"))
    date_registration = models.DateField(verbose_name=_("Registration deadline"))
    date_retraction = models.DateField(verbose_name=_("Retraction deadline"))

    # Other details
    cost = models.IntegerField(verbose_name=_("Cost in €"))
    max_participants = models.PositiveSmallIntegerField(verbose_name=_("Maximum participants"))
    information = RichTextField(verbose_name=_("Information about the event"))
    terms = models.ManyToManyField(Terms, verbose_name=_("Terms"), related_name="event", blank=True)
    info_mailings = models.ManyToManyField(
        InfoMailing, verbose_name=_("Info mailings"), related_name="events", blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.linked_group.short_name:
                self.slug = slugify(self.linked_group.short_name)
            else:
                self.slug = slugify(self.display_name)

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.display_name

    def can_register(self, request=None):
        now = datetime.today().date()

        if request and request.user.is_authenticated:
            if request.user.person in self.linked_group.members.all():
                return False

            if EventRegistration.objects.filter(person=request.user.person).exists():
                return False

            if (
                Voucher.objects.filter(event=self, person=request.user.person, used=False).count()
                > 0
            ):
                return True

        if self.linked_group.members.count() >= self.max_participants:
            return False

        if self.date_registration:
            return self.date_registration >= now
        return self.date_event > now

    def get_absolute_url(self):
        return reverse("event_by_name", kwargs={"slug": self.slug})

    @property
    def booked_percentage(self):
        return self.linked_group.members.count() / self.max_participants * 100

    @property
    def members_persons(self):
        return self.linked_group.members.all()

    @property
    def owners_persons(self):
        return self.linked_group.owners.all()

    @classmethod
    def upcoming_published_events(cls):
        return Event.objects.filter(published=True, date_event__gte=now())


class Voucher(ExtensibleModel):
    class Meta:
        verbose_name = _("Vouchers")
        verbose_name_plural = _("Vouchers")

    code = models.CharField(max_length=8, blank=True, default="")
    event = models.ForeignKey(
        Event,
        related_name="vouchers",
        verbose_name=_("Event"),
        on_delete=models.CASCADE,
        null=True,
    )
    person = models.ForeignKey(
        Person,
        related_name="vouchers",
        verbose_name=_("Person"),
        on_delete=models.CASCADE,
    )
    discount = models.IntegerField(default=100)

    used = models.BooleanField(default=False)
    used_person_uid = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("Used by"),
        related_name="used_vouchers",
        null=True,
    )
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_random_code(5, 3)
        super().save(*args, **kwargs)


class EventRegistration(ExtensibleModel):

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, verbose_name=_("Event"), related_name="registrations"
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_("Person"))
    date_registered = models.DateTimeField(auto_now_add=True, verbose_name=_("Registration date"))

    school = models.CharField(verbose_name=_("Name of school"), max_length=255)
    school_class = models.CharField(verbose_name=_("School class"), max_length=255)
    school_place = models.CharField(verbose_name=_("Place of the school"), max_length=255)

    comment = models.TextField(verbose_name=_("Comment / remarks"), blank=True, default="")
    medical_information = models.TextField(
        verbose_name=_("Medical information / intolerances"), blank=True, default=""
    )
    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        verbose_name=_("Voucher"),
        blank=True,
        null=True,
    )
    donation = models.PositiveIntegerField(verbose_name=_("Donation"), blank=True, null=True)
    accepted_terms = models.ManyToManyField(
        Terms,
        verbose_name=_("Accepted terms"),
        related_name="registrations",
    )

    accept_sepa = models.BooleanField(verbose_name=_("SEPA direct debit"))
    iban = IBANField(
        verbose_name=_("IBAN (for SEPA direct debit)"),
        enforce_database_constraint=True,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.event}, {self.person.first_name} {self.person.last_name}"

    class Meta:
        verbose_name = _("Event registration")
        verbose_name_plural = _("Event registrations")
        constraints = [
            models.UniqueConstraint(
                fields=["person", "event"], name="unique_person_registration_per_event"
            )
        ]
