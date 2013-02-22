-- these are all the new unmatched ones from the latest load
insert into matchbox_entityattribute (entity_id, namespace, value) values
    ('06bbed399832446c90a208624b9c8be6', 'urn:pogo:contractor', 205),
    ('c2daded88a9f4cc78cd513b0bf4c43fc', 'urn:pogo:contractor', 208),
    ('5516ba695ba741ab9f6ff35627621297', 'urn:pogo:contractor', 211),
    ('2114190913394f028f6bf74ae0d7a802', 'urn:pogo:contractor', 209),
    ('a515187b2bdd455595d8a2df805f7816', 'urn:pogo:contractor', 206),
    ('6a2f5a216da4454198a2265b4955ff5d', 'urn:pogo:contractor', 212),
    ('8c260a7c04c24e4187b7fa0dfcf5d384', 'urn:pogo:contractor', 210)
;
-- these are the old unmatched ones. time to fix.

insert into matchbox_entityattribute (entity_id, namespace, value) values
    ('0366453d2f1940e085c85d2df0c8d00b', 'urn:pogo:contractor', 168),
    ('a9c9ae97bf5346cca1e3afef229b627d', 'urn:pogo:contractor', 144),
    ('42dcdc63241e4679b13a96f9d42c216b', 'urn:pogo:contractor', 103),
    ('df222dee4ec94db7bb45e4b29bd40037', 'urn:pogo:contractor', 102),
    ('d473e580c5684a658b754eb97566cb05', 'urn:pogo:contractor', 172),
    ('fdb1b36821774c098680d5f298329114', 'urn:pogo:contractor', 167),
    ('a86b3b2f5ba2446485dd3024ac7f6f47', 'urn:pogo:contractor', 198),
    ('34f626b8d4224cf8ba6c3126d112b366', 'urn:pogo:contractor', 123),
    ('bb02df3a5d9e4ca0a554bdeb9e8309d6', 'urn:pogo:contractor', 114),
    ('ef389f39acc141b7a9b554048ae9d95d', 'urn:pogo:contractor', 19),
    ('93a5e58ab8e94bd8af78edc8b4ae894c', 'urn:pogo:contractor', 120),
    ('386f2ae1d9174746a6ab66cfccb43216', 'urn:pogo:contractor', 92),
    ('46a43aff0a6743c59fbebd588e8ee743', 'urn:pogo:contractor', 170),
    ('b8b8df9b97a84b18add9f875fe0f7f34', 'urn:pogo:contractor', 112),
    ('4c77d12581dd42358edeada899f3caba', 'urn:pogo:contractor', 65),
    ('4338172ef2ac4219bfcd07972f11613a', 'urn:pogo:contractor', 88),
    ('d15a73ceb3b046e0bf127ee0bf8c9b5f', 'urn:pogo:contractor', 81),
    ('e5d1de1c3fdb487eaa83dacf7cb304f5', 'urn:pogo:contractor', 28),
    ('a7e5453e8f2a40fcb4ce24bb2baa5a73', 'urn:pogo:contractor', 186),
    ('946e265539044328b43a441d7fb9e02a', 'urn:pogo:contractor', 163),
    ('575b2a6ec0e4408c9b95e142ecec2da1', 'urn:pogo:contractor', 176),
    ('8e0f1a54d1b445daaf5e549a13410145', 'urn:pogo:contractor', 132),
    ('e2f19ff3ff504b5aaf75cc581d32da2e', 'urn:pogo:contractor', 113),
    ('302ad21e591a476192de2cf68f73872e', 'urn:pogo:contractor', 122),
    ('2af84ca045ee4a66a0162d9f2e8101e2', 'urn:pogo:contractor', 63),
    ('33ba2ac35bce41b49dc037cf62e48442', 'urn:pogo:contractor', 166),
    ('f4b5d8ad31c74373ba665a37ac8415fe', 'urn:pogo:contractor', 111),
    ('888e893cbc424e818ec86cc37f16a611', 'urn:pogo:contractor', 109),
    ('e78f1ee68e164caf93a9e4f268f4433b', 'urn:pogo:contractor', 158)
;

-- add this entity which was merged, Creative Associates International

insert into matchbox_entityattribute(entity_id, namespace, value) values ('01b0b757-614c-4077-916d-366400d286ce', 'urn:pogo:contractor', 203);
