/* 
  This is a queue of nimsp salt contributors. Unused entries will
  have ContributionID and SaltID as null.
*/
CREATE TABLE Salts (
  ID SERIAL,
  ContributionID bigint DEFAULT NULL,
  SaltID bigint DEFAULT NULL,
  Amount Numeric(12,2) DEFAULT NULL,
  Date date default NULL,
  Contributor varchar(255) NOT NULL,
  NewContributor varchar(255) NOT NULL,
  First varchar(124) NOT NULL default '',
  Last varchar(75) NOT NULL default '',
  Occupation varchar(255) DEFAULT NULL,
  Employer varchar(255) DEFAULT NULL,
  NewEmployer varchar(255) DEFAULT NULL,
  Address varchar(100) DEFAULT NULL,
  NewAddress varchar(150) DEFAULT NULL,
  City varchar(50) NOT NULL,
  State char(2) NOT NULL,
  ZipCode varchar(10) NOT NULL,
  CatCode varchar(5) DEFAULT NULL,
  RecipientReportsBundleId INTEGER DEFAULT NULL,
  PRIMARY KEY (ID)
);
