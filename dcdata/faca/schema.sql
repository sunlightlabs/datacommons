-- tables need to be populated with the CSVs extracted from the MS Access DB with the mdb-export command

CREATE TABLE faca_agencies
 (
	AID			Int8 primary key, 
	ANo			Int8, 
	FY			varchar(8), 
	AgencyAbbr			varchar(12), 
	AgencyName			varchar(400), 
	Address1			varchar(100), 
	Address2			varchar(100), 
	City			varchar(100), 
	State			varchar(100), 
	Zipcode			varchar(100), 
	Classification			varchar(100), 
	Prefix			varchar(20), 
	FirstName			varchar(30), 
	MiddleName			varchar(30), 
	LastName			varchar(40), 
	Suffix			varchar(20), 
	Title			varchar(510), 
	Phone			varchar(40), 
	Fax			varchar(30), 
	EMail			varchar(508), 
	AgencyURL			text, 
	DMPrefix			varchar(20), 
	DMFirstName			varchar(30), 
	DMMiddleName			varchar(30), 
	DMLastName			varchar(40), 
	DMSuffix			varchar(20), 
	DMTitle			varchar(510), 
	DMPhone			varchar(40), 
	DMFax			varchar(30), 
	DMEMail			varchar(508)
);



CREATE TABLE faca_committees
 (
	CID			Int8 primary key, 
	CNo			Int8, 
	AID			Int8, 
	ANo			Int8, 
	GID			Int8, 
	FY			varchar(8), 
	CommitteeName			varchar(510), 
	OriginalEstablishmentDate			varchar(100), 
	TerminationDate			varchar(100), 
	Prefix			varchar(20), 
	FirstName			varchar(30), 
	MiddleName			varchar(30), 
	LastName			varchar(40), 
	Suffix			varchar(20), 
	Title			varchar(510), 
	Phone			varchar(40), 
	Fax			varchar(30), 
	EMail			varchar(508), 
	PCID			Int8, 
	DMPrefix			varchar(20), 
	DMFirstName			varchar(30), 
	DMMiddleName			varchar(30), 
	DMLastName			varchar(40), 
	DMSuffix			varchar(20), 
	DMTitle			varchar(510), 
	DMPhone			varchar(40), 
	DMFax			varchar(30), 
	DMEMail			varchar(510), 
	AdminInactive			varchar(2)
);


CREATE TABLE faca_generalinformation
 (
	ID			Int8, 
	CID			Int8, 
	CNo			Int8, 
	FY			varchar(8), 
	DepartmentOrAgency			varchar(10), 
	NewCommittee			varchar(6), 
	CurrentCharterDate			varchar(100), 
	DateOfRenewalCharter			varchar(100), 
	DateToTerminate			varchar(100), 
	TerminatedThisFY			varchar(6), 
	SpecificTerminationAuthority			varchar(100), 
	ActualTerminationDate			varchar(100), 
	EstablishmentAuthority			varchar(60), 
	SpecificEstablishmentAuthority			varchar(200), 
	EffectiveDateOfAuthority			varchar(100), 
	CommitteeType			varchar(30), 
	Presidential			varchar(6), 
	CommitteeFunction			varchar(100), 
	CommitteeStatus			varchar(20), 
	CommitteeURL			text, 
	ExemptRenew			varchar(6), 
	PresidentialAppointments			varchar(6), 
	MaxNumberofMembers			varchar(20)
);


CREATE TABLE faca_members
 (
	MembersID			Int8 primary key, 
	CID			Int8, 
	CNo			Int8, 
	FY			varchar(8), 
	Prefix			varchar(20), 
	FirstName			varchar(30), 
	MiddleName			varchar(30), 
	LastName			varchar(40), 
	Suffix			varchar(20), 
	Chairperson			varchar(6), 
	OccupationOrAffiliation			varchar(510), 
	StartDate			varchar(100), 
	EndDate			varchar(100), 
	AppointmentType			varchar(100), 
	AppointmentTerm			varchar(100), 
	PayPlan			varchar(140), 
	PaySource			varchar(100), 
	MemberDesignation			varchar(100), 
	RepresentedGroup			varchar(508)
);

create index faca_members_cid on faca_members (CID);
    
CREATE TABLE faca_matches
(
    MembersID Int8 references faca_members,
    entity_id uuid references matchbox_entity on delete cascade
);
