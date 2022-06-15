from SupportTicketSystem.common_queries import *

'''
Test common database query methods.
    1. Inputs expecting defined output
    2. Inputs expecting None or 0 output
'''

def test_read_users_groups(client, init_large_database):
    with client as test_client:
        assert len(read_users_groups(1)) == 1
        assert len(read_users_groups(2)) == 2
        for group, id in zip(read_users_groups(2), [1,2]):
            assert group.id == id
        assert not read_users_groups(6) #no groups
        
def test_all_users_in_group(client, init_large_database):
    with client as test_client:
        assert len(read_all_users_in_group(1)) == 5
        assert len(read_all_users_in_group(2)) == 3
        assert len(read_all_users_in_group(3)) == 1
        for user, id in zip(read_all_users_in_group(1), [1,2,3,4,5]):
            assert user.id == id
        assert not read_all_users_in_group(4) #empty group

def test_all_groups_not_userin(client, init_large_database):
    with client as test_client:
        print(read_all_groups_not_userin(1).all())
        assert len(read_all_groups_not_userin(1).all()) == 3
        assert len(read_all_groups_not_userin(2).all()) == 2
        ug = create_user_group(db, 4, 4)
        assert len(read_all_groups_not_userin(4).all()) == 0
        delete_user_group(db, ug.user_id, ug.group_id)

def test_read_all_tickets_in_group(client, init_large_database):
    with client as test_client:
        assert len(read_all_tickets_in_group(1)) == 3
        assert len(read_all_tickets_in_group(2)) == 2
        assert len(read_all_tickets_in_group(3)) == 0
        assert len(read_all_tickets_in_group(4)) == 0
        
def test_read_rank(client, init_large_database):
    with client as test_client:
        assert read_rank(1,1).rank_in_group == 2
        assert read_rank(3,1).rank_in_group == 0
        assert read_rank(2,1).rank_in_group == 1

def test_all_unrestickets_for_user(client, init_large_database):
    with client as test_client:
        assert len(list(all_unrestickets_for_user(1))) == 1
        assert len(list(all_unrestickets_for_user(2))) == 2
        assert len(list(all_unrestickets_for_user(6))) == 0

def test_all_unrestickets_by_user(client, init_large_database):
    with client as test_client:
        assert len(list(all_unrestickets_by_user(1))) == 2
        assert len(list(all_unrestickets_by_user(2))) == 1
        assert len(list(all_unrestickets_by_user(3))) == 0

def test_all_tickets_by_user(client, init_large_database):
    with client as test_client:
        assert len(list(all_tickets_by_user(3))) == 0
        assert len(list(all_tickets_by_user(2))) == 2
        assert len(list(all_tickets_by_user(1))) == 3

def test_read_username(client, init_large_database):
    with client as test_client:
        assert read_username(1) == "username1"
        assert read_username(2) == "username2"
        assert read_username(3) == "username3"
        assert read_username(4) == "username4"