DROP TABLE IF EXISTS federal_fortune_x_hundred;

CREATE TABLE federal_fortune_x_hundred (
        rank INTEGER NOT NULL, 
        organization VARCHAR NOT NULL, 
        ie_id UUID NOT NULL, 
        donor_total NUMERIC(15,2), 
        lobby_total numeric(15,2), 
        influence_total numeric(15,2), 
        incumbent_pct VARCHAR(10), 
        federal_biz_total numeric(15,2), 
        federa_aid_total numeric(15,2), 
        effective_tax_rate VARCHAR(10), 
        tax_link VARCHAR(100), 
        state_subsidy_link VARCHAR(100)
);

