from db_classes.classes_si_db.smartpots import SmartPots
from db_classes.classes_si_db.user import Users


def assign_pot_to_user(pot: SmartPots, user: Users):
    """
    Assign an HubGroup object to a user given his user id
    :param pot:
    :param user:
    :return: nothing
    """
    user.pots.append(pot)
    user.save()

def delete_pot(pot: SmartPots):
    """
    Used when a user is deleted, or he removes a group from his account
    :return: nothing
    """
    pot.delete()


def delete_user(user: Users):
    """
    Used when a user delete his account, his groups and hubs are then deleted as well
    :return: nothing
    """
    for pot in user.pots:
        delete_pot(pot)
    user.delete()
