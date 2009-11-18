/* 
  This is a queue of nimsp salt contributors. Unused entries will
  have ContributionID and SaltID as null.
*/
CREATE TABLE Salts (
  ID SERIAL,
  ContributionID BIGINT DEFAULT NULL,
  SaltID BIGINT DEFAULT NULL,
  Amount Numeric(12,2) DEFAULT NULL,
  Date date default NULL,
  Contributor varchar(255) NOT NULL,
  Occupation varchar(255) DEFAULT NULL,
  Employer varchar(255) DEFAULT NULL,
  Address varchar(100) DEFAULT NULL,
  City varchar(50) NOT NULL,
  State char(2) NOT NULL,
  ZipCode varchar(10) NOT NULL,
  CatCode varchar(5) DEFAULT NULL,
  PRIMARY KEY (ID)
);
