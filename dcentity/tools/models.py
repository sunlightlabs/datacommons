from collections import defaultdict

from django.db import models, connection

from dcentity.models import Entity, EntityAlias
from dcentity.tools.names import fix_name, PersonName, OrganizationName
from dcentity.tools.utils import expand_state

class PoliticianManager(models.Manager):
    def get_query_set(self):
        return super(PoliticianManager, self).get_query_set().filter(type='politician')

    def get_unique_politician(self, name):
        """
        Given an entity name, return a (name, entity) tuple of a politician
        whose name uniquely matches the given name.  If no unique politician is
        found, return None.
        """
        if isinstance(name, OrganizationName):
            name = name.pname

        if not name:
            return None

        last_name_matches = self.get_query_set().filter(
                aliases__alias__icontains=name.last).distinct()
        name_matches = []
        for entity in last_name_matches:
            for check in entity.names:
                if check == name:
                    name_matches.append((check, entity))
                    break

        # Operating under the assumption that we may have multiple entities for
        # a single politician, check to make sure that all name_matches match
        # each other.  If any of the matched names doesn't fuzzily match the
        # other results, we don't have a unique politician.
        if name_matches:
            first_name, first_entity = name_matches[0]
            for n, entity in name_matches[1:]:
                if not first_entity.some_name_matches(entity):
                    break
            else:
                return (first_name, first_entity)
        return None

class EntityPlus(Entity):
    """
    Proxy model for Entity with extra methods for fuzzy name matching and
    search terms.
    """

    politicians = PoliticianManager()

    _names = None
    def _get_names(self):
        if self._names is None:
            self._names = []
            fixed_names = set(fix_name(alias.alias) for alias in self.aliases.all())
            for name in fixed_names:
                if self.type in ['politician', 'individual']:
                    self._names.append(PersonName(name))
                elif self.type == 'organization':
                    self._names.append(OrganizationName(name))
        return self._names

    def _set_names(self):
        self._names = _names

    # List of fuzzy name classes for each alias
    names = property(_get_names, _set_names)

    def get_search_terms(self, name):
        """
        The goal: a first name, last name, and state.  If we are a politician
        or organization that represents a politician (e.g. a pac), get the
        state and alias from the politician.  Otherwise, just fall back to the
        name.
        """
        pol_entity = None
        if self.type == 'politician':
            pol_entity = self
        elif isinstance(name, OrganizationName) and name.is_politician():
            match = EntityPlus.politicians.get_unique_politician(name)
            if match:
                name, pol_entity = match

        search_terms = [name.search_string()]
        if pol_entity:
            search_terms.append(
                expand_state(pol_entity.politician_metadata.state)
            )
        return " ".join(search_terms)

    def first_matching_name(self, entity):
        """
        Returns the first alias from entity that matches an alias in self, or
        None if no such alias is found.

        Returns the first alias from entity that matches an alias in self, or
        None if no such alias is found.
        >>> e1 = EntityPlus.objects.create(type="politician", name="name")
        >>> a = e1.aliases.create(alias="WAYNE P GRETSKY")
        >>> a = e1.aliases.create(alias="Mr D")
        >>> e2 = EntityPlus.objects.create(type="politician", name="Fantastick")
        >>> a = e2.aliases.create(alias="Yer Mom")
        >>> a = e2.aliases.create(alias="W Gretsky")
        >>> e1.first_matching_name(e2)
        <PersonName("W Gretsky")>

        >>> e3 = EntityPlus.objects.create(type="politician", name="yah")
        >>> a = e3.aliases.create(alias="W P Fargo")
        >>> print e1.first_matching_name(e3)
        None
        """
        for them in entity.names:
            for us in self.names:
                if us == them:
                    return them
        return None

    def some_name_matches(self, entity):
        """
        Returns true if there is some name somewhere in self that fuzzily
        matches some name somewhere in the given entity.
        """
        return bool(self.first_matching_name(entity))

    class Meta:
        proxy = True
        ordering = ['name']
