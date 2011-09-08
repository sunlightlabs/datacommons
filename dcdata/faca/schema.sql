

CREATE TABLE faca_agencies
 (
	AID			Int8 primary key, 
	ANo			Int8, 
	FY			Char (8), 
	AgencyAbbr			Char (12), 
	AgencyName			Char (400), 
	Address1			Char (100), 
	Address2			Char (100), 
	City			Char (100), 
	State			Char (100), 
	Zipcode			Char (100), 
	Classification			Char (100), 
	Prefix			Char (20), 
	FirstName			Char (30), 
	MiddleName			Char (30), 
	LastName			Char (40), 
	Suffix			Char (20), 
	Title			Char (510), 
	Phone			Char (40), 
	Fax			Char (30), 
	EMail			Char (508), 
	AgencyURL			text, 
	DMPrefix			Char (20), 
	DMFirstName			Char (30), 
	DMMiddleName			Char (30), 
	DMLastName			Char (40), 
	DMSuffix			Char (20), 
	DMTitle			Char (510), 
	DMPhone			Char (40), 
	DMFax			Char (30), 
	DMEMail			Char (508)
);



CREATE TABLE faca_committees
 (
	CID			Int8 primary key, 
	CNo			Int8, 
	AID			Int8, 
	ANo			Int8, 
	GID			Int8, 
	FY			Char (8), 
	CommitteeName			Char (510), 
	OriginalEstablishmentDate			varchar(100), 
	TerminationDate			varchar(100), 
	Prefix			Char (20), 
	FirstName			Char (30), 
	MiddleName			Char (30), 
	LastName			Char (40), 
	Suffix			Char (20), 
	Title			Char (510), 
	Phone			Char (40), 
	Fax			Char (30), 
	EMail			Char (508), 
	PCID			Int8, 
	DMPrefix			Char (20), 
	DMFirstName			Char (30), 
	DMMiddleName			Char (30), 
	DMLastName			Char (40), 
	DMSuffix			Char (20), 
	DMTitle			Char (510), 
	DMPhone			Char (40), 
	DMFax			Char (30), 
	DMEMail			Char (510), 
	AdminInactive			Char (2)
);


CREATE TABLE faca_generalinformation
 (
	ID			Int8, 
	CID			Int8, 
	CNo			Int8, 
	FY			Char (8), 
	DepartmentOrAgency			Char (10), 
	NewCommittee			Char (6), 
	CurrentCharterDate			varchar(100), 
	DateOfRenewalCharter			varchar(100), 
	DateToTerminate			varchar(100), 
	TerminatedThisFY			Char (6), 
	SpecificTerminationAuthority			Char (100), 
	ActualTerminationDate			varchar(100), 
	EstablishmentAuthority			Char (60), 
	SpecificEstablishmentAuthority			Char (200), 
	EffectiveDateOfAuthority			varchar(100), 
	CommitteeType			Char (30), 
	Presidential			Char (6), 
	CommitteeFunction			Char (100), 
	CommitteeStatus			Char (20), 
	CommitteeURL			text, 
	ExemptRenew			Char (6), 
	PresidentialAppointments			Char (6), 
	MaxNumberofMembers			Char (20)
);


CREATE TABLE faca_members
 (
	MembersID			Int8 primary key, 
	CID			Int8, 
	CNo			Int8, 
	FY			Char (8), 
	Prefix			Char (20), 
	FirstName			Char (30), 
	MiddleName			Char (30), 
	LastName			Char (40), 
	Suffix			Char (20), 
	Chairperson			Char (6), 
	OccupationOrAffiliation			Char (510), 
	StartDate			varchar(100), 
	EndDate			varchar(100), 
	AppointmentType			Char (100), 
	AppointmentTerm			Char (100), 
	PayPlan			Char (140), 
	PaySource			Char (100), 
	MemberDesignation			Char (100), 
	RepresentedGroup			Char (508)
);

create index faca_members_cid on faca_members (CID);
    
CREATE TABLE faca_matches
(
    MembersID Int8 references faca_members,
    entity_id uuid references matchbox_entity on delete cascade
);
