create view lobbyist_bundling_unified_view as select * from contribution_bundle inner join contribution_lobbyistbundle on file_num = file_num_id
;
