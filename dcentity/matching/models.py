from common.db.fields.uuid_field import UUIDField
from django.db import models
import uuid

class Officer(models.Model):
    id = UUIDField(primary_key=True, auto=True, default=uuid.uuid4().hex)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=255, blank=True, null=True)
    ein = models.CharField(max_length=10)
    xml_document_id = models.IntegerField()
    organization_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'guidestar_officer'


class WhiteHouseVisitor(models.Model):
    first_name = models.CharField(max_length=64)
    middle_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    class Meta:
        db_table = 'whitehouse_visitor'

    def build_name(self):
        return ' '.join([ x for x in [self.first_name, self.middle_name, self.last_name] if x])

    name = property(build_name)


class HonorariumRegistrant(models.Model):
    registrant_ext_id = models.IntegerField()
    name = models.CharField(max_length=200)
    total_given = models.BigIntegerField()

    class Meta:
        db_table = 'honorarium_registrant'


class AlecSponsor(models.Model):
    name = models.CharField(max_length=200)
    state = models.CharField(max_length=2)
    is_cosponsor = models.BooleanField(default=False)

    class Meta:
        db_table = 'alec_sponsor'


class Fortune100Company(models.Model):
    rank = models.SmallIntegerField(null=False)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'fortune_100'


class USNewsTop200University(models.Model):
    rank = models.SmallIntegerField(null=False)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'us_news_200_unis'


class ConsumerGroup(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'consumer_group'

class HillStaffer(models.Model):
    name = models.CharField(max_length=100)
    office = models.CharField(max_length=100)
    member_bioguide_id = models.CharField(max_length=7, null=True)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = 'hill_staffer'

class PublicCompany(models.Model):
    name = models.CharField(max_length=100)
    gvkey = models.IntegerField()
    ticker = models.CharField(max_length=10, null=True)
    naics = models.IntegerField(null=True)
    sic = models.IntegerField(null=True)
    state = models.CharField(max_length=2, null=True)

    class Meta:
        db_table = 'public_company'


class MemberOfCongressWithBioguide(models.Model):
    bioguide_id = models.CharField(max_length=12)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    district = models.SmallIntegerField(null=True)
    cycle = models.SmallIntegerField()

    class Meta:
        db_table = 'moc_bioguide'

    def build_name(self):
        return ' '.join([self.first_name, self.last_name])

    def pad_district(self):
        if self.district < 10:
            return '0{0}'.format(self.district)
        else:
            return str(self.district)

    name = property(build_name)
    padded_district = property(pad_district)


class LocalElectionOfficial(models.Model):
    state = models.CharField(max_length=64)
    board = models.CharField(max_length=255, null=True)
    office = models.CharField(max_length=64, null=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'local_election_officials'


class ContributorsByStateForLEO(models.Model):
    """
    create table tmp_akr_leo_names_by_state as (
        select distinct contributor_name as name, contributor_state as state, contributor_employer as employer, contributor_occupation as occupation, contributor_city as city
        from contribution_contribution
        where contributor_type = 'I' and cycle in (2010, 2012)
    );
    """
    name = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=2, db_index=True)
    employer = models.CharField(max_length=255, blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'leo_matching_contrib_names_by_state'


class SuperPACDonor(models.Model):
    """
    create table research__superpac_donors as
        select contributor_name as name, string_agg(trim(both from committee_id), ',') as committee_ids, string_agg(trim(both from committee_name), ',') as committee_names
        from fec_committee_itemized
        where committee_type = 'O' and contributor_name is not null
        group by contributor_name;

    alter table research__superpac_donors add column id serial;
    """

    name = models.CharField(max_length=200)
    committee_ids = models.CharField(max_length=255)
    committee_names = models.CharField(max_length=255)

    class Meta:
        db_table = 'research__superpac_donors'



