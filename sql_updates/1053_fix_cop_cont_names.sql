update matchbox_entity set name = replace(name, ' (COP CONT ),', ',') where name like '%(COP CONT )%';
update matchbox_entityalias set alias = replace(alias, ' (COP CONT ),', ',') where alias like '%(COP CONT )%';
