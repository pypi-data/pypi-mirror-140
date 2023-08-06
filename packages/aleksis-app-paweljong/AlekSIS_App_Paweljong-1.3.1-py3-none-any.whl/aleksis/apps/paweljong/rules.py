import rules

from aleksis.core.models import Group
from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
    is_group_member,
)

from .models import Event, EventRegistration, Terms, Voucher
from .predicates import (
    is_own_registration,
    is_own_voucher,
    see_group_by_grouptype,
    see_owned_groups_members,
)

# View vouchers
view_vouchers_predicate = has_person & (
    has_global_perm("paweljong.view_voucher") | has_any_object("paweljong.view_voucher", Voucher)
)
rules.add_perm("paweljong.view_vouchers_rule", view_vouchers_predicate)

# Edit vouchers
change_vouchers_predicate = has_person & (
    has_global_perm("paweljong.change_voucher")
    | has_any_object("paweljong.change_voucher", Voucher)
)
rules.add_perm("paweljong.change_vouchers_rule", change_vouchers_predicate)


# Delete vouchers
delete_vouchers_predicate = has_person & (
    has_global_perm("paweljong.delete_voucher")
    | has_any_object("paweljong.delete_voucher", Voucher)
)
rules.add_perm("paweljong.delete_vouchers_rule", delete_vouchers_predicate)

# Create vouchers
create_vouchers_predicate = has_person & (
    has_global_perm("paweljong.create_voucher")
    | has_any_object("paweljong.create_voucher", Voucher)
)
rules.add_perm("paweljong.create_vouchers_rule", create_vouchers_predicate)

# Edit events
change_events_predicate = has_person & (
    has_global_perm("paweljong.change_event") | has_any_object("paweljong.change_event", Event)
)
rules.add_perm("paweljong.change_events_rule", change_events_predicate)


# Delete events
delete_events_predicate = has_person & (
    has_global_perm("paweljong.delete_event") | has_any_object("paweljong.delete_event", Event)
)
rules.add_perm("paweljong.delete_events_rule", delete_events_predicate)

# Create events
create_events_predicate = has_person & (
    has_global_perm("paweljong.create_event") | has_any_object("paweljong.create_event", Event)
)
rules.add_perm("paweljong.create_events_rule", create_events_predicate)

# Allowed to see group
may_see_group_predicate = has_person & (
    is_group_member | has_any_object("core.view_group", Group) | see_group_by_grouptype
)
rules.add_perm("paweljong.may_see_group_rule", may_see_group_predicate)

may_see_person_predicate = has_person & (
    see_owned_groups_members | has_object_perm("core.view_person")
)
rules.add_perm("paweljong.see_person_rule", may_see_person_predicate)

# View registrations
view_registrations_predicate = has_person & (
    has_global_perm("paweljong.view_eventregistration")
    | has_any_object("paweljong.view_eventregistration", EventRegistration)
)
rules.add_perm("paweljong.view_registrations_rule", view_registrations_predicate)


# Manage registrations
manage_registrations_predicate = has_person & (
    has_global_perm("paweljong.manage_registration")
    | is_own_registration
    | has_any_object("paweljong.manage_registration", EventRegistration)
)
rules.add_perm("paweljong.manage_registrations_rule", manage_registrations_predicate)

# Delete registrations
delete_registrations_predicate = has_person & (
    has_global_perm("paweljong.delete_eventregistration")
    | has_any_object("paweljong.delete_eventregistration", EventRegistration)
)
rules.add_perm("paweljong.delete_registrations_rule", delete_registrations_predicate)


# Is own voucher?
is_own_voucher_predicate = has_person & (is_own_voucher)
rules.add_perm("paweljong.is_own_voucher_rule", is_own_voucher_predicate)


# View terms
view_terms_predicate = has_person & (
    has_global_perm("paweljong.view_term") | has_any_object("paweljong.view_term", Terms)
)
rules.add_perm("paweljong.view_terms_rule", view_terms_predicate)


# View info_mailings
view_info_mailings_predicate = has_person & (
    has_global_perm("paweljong.view_info_mailing")
    | has_any_object("paweljong.view_info_mailing", Terms)
)
rules.add_perm("paweljong.view_info_mailings_rule", view_info_mailings_predicate)
