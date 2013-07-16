from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
import time
from secretballot.managers import VotableManager
try:
    from django.contrib.auth import get_user_model
except ImportError:
    # Django < 1.5
    from django.contrib.auth.models import User
    get_user_model = lambda: User

DEFAULT_VOTE_CHOICES = (
    (+1, '+1'),
    (-1, '-1'),
)

VOTE_CHOICES = getattr(settings, 'VOTE_CHOICES', DEFAULT_VOTE_CHOICES)

class Vote(models.Model):
    user = models.ForeignKey(get_user_model())
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    # generic foreign key to the model being voted upon
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    timestamp = models.BigIntegerField(default=int(time.time()))
    votes_name = models.CharField(max_length=190,null=False,default="",db_index=True)
    objects = VotableManager()
    class Meta:
        unique_together = (('user', 'content_type', 'object_id','votes_name'),)

    def __unicode__(self):
        return '%s from %s on %s' % (self.get_vote_display(), self.user,
                                     self.content_object)
