__author__ = "James Turk (jturk@sunlightfoundation.com)"
__version__ = "0.2.3"
__copyright__ = "Copyright (c) 2009 Sunlight Labs"
__license__ = "BSD"

from django.contrib.contenttypes import generic
import time
from secretballot.managers import VotableManager


def limit_total_votes(num):
    from secretballot.models import Vote
    def total_vote_limiter(request, content_type, object_id, vote):
        return Vote.objects.filter(content_type=content_type,
                               user=request.user).count() < num
    return total_vote_limiter

def enable_voting_on(cls, manager_name='objects',
                    votes_name='votes',
                    upvotes_name='total_upvotes',
                    downvotes_name='total_downvotes',
                    total_name='vote_total',
                    add_vote_name='add_vote',
                    remove_vote_name='remove_vote',
                    base_manager=None):
    from secretballot.models import Vote
    VOTE_TABLE = Vote._meta.db_table

    def add_vote(self, user, vote):
        voteobj, created = getattr(self, votes_name).get_or_create(user=user,
            defaults={'vote':vote, 'content_object':self,'votes_name':votes_name})
        if not created:
            voteobj.vote = vote
            
        voteobj.timestamp = int(time.time())
        voteobj.save()

    def remove_vote(self, user):
        getattr(self, votes_name).filter(user=user,votes_name=votes_name).delete()

    def get_total(self):
        if not hasattr(self, upvotes_name) or not hasattr(self, downvotes_name):
            from django.db.models import Sum
            return getattr(self, votes_name).filter(votes_name=votes_name).aggregate(Sum('vote'))['vote__sum']
        return getattr(self, upvotes_name) - getattr(self, downvotes_name)

    

    cls.add_to_class(manager_name, VotableManager())
    cls.add_to_class(votes_name, generic.GenericRelation(Vote, related_name="%s_%s" % (cls._meta.app_label,votes_name)))
    # do i need total_name? maybe not?
    # cls.add_to_class(total_name, property(get_total)) 
    cls.add_to_class(add_vote_name, add_vote)
    cls.add_to_class(remove_vote_name, remove_vote)
