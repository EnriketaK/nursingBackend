from django.urls import re_path 
from tutorials import views
 
urlpatterns = [ 
    re_path (r'^api/nursing$', views.forms_list),
    re_path (r'^api/nursing/suggestion$', views.get_suggestion),
    re_path (r'^api/nursing/save-admission$', views.save_admission_form),
    re_path (r'^api/nursing/save-summary$', views.save_summary),
    re_path (r'^api/nursing/(?P<pk>[0-9]+)$', views.form_detail),
    re_path (r'^api/nursing/summaries/formId/(?P<pk>[0-9]+)$', views.get_summaries),
    re_path (r'^api/nursing/translated-sum$', views.get_translated_summaries),
]