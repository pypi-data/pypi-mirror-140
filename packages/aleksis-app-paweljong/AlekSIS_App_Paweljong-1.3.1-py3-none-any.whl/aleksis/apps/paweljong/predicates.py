from django.contrib.auth import get_user_model

from rules import predicate

from aleksis.core.models import Group, Person
from aleksis.core.util.predicates import check_object_permission

from .models import EventRegistration, Voucher

User = get_user_model()


@predicate
def see_group_by_grouptype(user: User, group: Group) -> bool:
    """Predicate which checks if the user is allowed to see the groups GroupType."""
    grouptype = group.group_type

    return check_object_permission(user, "core.view_grouptype", grouptype)


@predicate
def see_owned_groups_members(user: User, person: Person) -> bool:
    """Owners of groups can see their members."""
    groups_list = user.person.owner_of.all().values_list("id", flat=True)

    return Person.member_of.filter(id__in=groups_list).exists()


@predicate
def is_own_voucher(user: User, voucher: Voucher) -> bool:
    """Predicate which checks if the voucher belongs to the user."""
    return voucher.person == user.person


@predicate
def is_own_registration(user: User, registration: EventRegistration) -> bool:
    """Predicate which checks if the registration belongs to the user."""
    return registration.person == user.person
