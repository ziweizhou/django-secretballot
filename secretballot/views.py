from django.template import loader, RequestContext
from django.core.exceptions import ImproperlyConfigured
from django.http import (HttpResponse, HttpResponseRedirect, Http404,
                         HttpResponseForbidden)
from django.db.models import get_model
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType
from secretballot.models import Vote
from django.db.models import Sum
import json

def vote(request, content_type, object_id, vote, can_vote_test=None,
              redirect_url=None, template_name=None, template_loader=loader,
              extra_context=None, context_processors=None, mimetype=None):

    user = request.user
    if not user.is_active:
        raise HttpResponseForbidden('Inactive users are not permitted to vote.')
    if isinstance(content_type, ContentType):
        pass
    elif isinstance(content_type, ModelBase):
        content_type = ContentType.objects.get_for_model(content_type)
    elif isinstance(content_type, basestring) and '.' in content_type:
        app, modelname = content_type.split('.')
        content_type = ContentType.objects.get(app_label=app, model__iexact=modelname)
    else:
        raise ValueError('content_type must be an instance of ContentType, a model, or "app.modelname" string')
    content_obj = None
    # do the action
    if vote:
        content_obj = content_type.model_class().objects.filter(pk=object_id)
        # 404 if object to be voted upon doesn't exist
        if content_obj.count() == 0:
            raise Http404

        # if there is a can_vote_test func specified, test then 403 if needed
        if can_vote_test:
            if not can_vote_test(request, content_type, object_id, vote):
                return HttpResponseForbidden("vote was forbidden")

        vobj,new = Vote.objects.get_or_create(content_type=content_type,
                                              object_id=object_id, user=user,
                                              defaults={'vote':vote})
        if not new:
            vobj.vote = vote
            vobj.save()
    else:
        Vote.objects.filter(content_type=content_type,
                            object_id=object_id, user=user).delete()

    # build the response
    if redirect_url:
        return HttpResponseRedirect(redirect_url)
    elif template_name:
        if content_obj is not None:
            content_obj = content_obj.get()
        else:
            content_type.model_class().objects.get(pk=object_id)
        c = RequestContext(request, {'content_obj':content_obj},
                           context_processors)

        # copy extra_context into context, calling any callables
        for k,v in extra_context.items():
            if callable(v):
                c[k] = v()
            else:
                c[k] = v

        t = template_loader.get_template(template_name)
        body = t.render(c)
    else:
        votes = Vote.objects.filter(content_type=content_type,
                                    object_id=object_id)
        num_votes = votes.count()
        rating = votes.aggregate(Sum('vote'))['vote__sum']
        body = json.dumps({"num_votes": num_votes, "rating": rating})

    return HttpResponse(body, mimetype=mimetype)
