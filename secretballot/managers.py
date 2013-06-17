
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text

class VotableManager(models.Manager):

    def get_queryset(self):
        # db_table = self.model._meta.db_table
        # pk_name = self.model._meta.pk.attname
        # content_type = ContentType.objects.get_for_model(self.model).id
        # downvote_query = '(SELECT COUNT(*) from %s WHERE vote=-1 AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
        # upvote_query = '(SELECT COUNT(*) from %s WHERE vote=1 AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
        return super(VotableManager, self).get_query_set()
    #     # return super(VotableManager, self).get_queryset().extra(
    #     #     select={upvotes_name: upvote_query,
    #     #             downvotes_name: downvote_query})

    # #TODO: update these to using django comment style on generic models.
    # def from_user(self, user):
    #     db_table = self.model._meta.db_table
    #     pk_name = self.model._meta.pk.attname
    #     content_type = ContentType.objects.get_for_model(self.model).id
    #     query = '(SELECT vote from %s WHERE user=%%s AND object_id=%s.%s AND content_type_id=%s)' % (VOTE_TABLE, db_table, pk_name, content_type)
    #     return self.get_queryset().extra(select={'user_vote': query},
    #                                       select_params=(user,))

    def from_request(self, request,model,votes_name):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured('To use secretballot a user must be authenticated')
        return self.from_user(request.user,model,votes_name)

    def for_model(self, model,votes_name):
        """
        QuerySet for all likes/bookmarks/votes for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_query_set().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_id=force_text(model._get_pk_val()),votes_name=votes_name)
        return qs

    def from_user(self,user,model,votes_name):

        """
        QuerySet for all likes/bookmarks/votes currently for a particular user
        """
        ct = ContentType.objects.get_for_model(model)
        return self.get_queryset().filter(user=user,content_type=ct,votes_name=votes_name)

    def total_count(self,model,votes_name):
        return self.for_model(model,votes_name).count()