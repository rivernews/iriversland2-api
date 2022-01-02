from django.conf import settings
from django.db import models

# from ckeditor_uploader.fields import RichTextUploadingField

from django.template.defaultfilters import truncatechars

from django.utils import timezone

class Document(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # or you can use '[from django.contrib.auth import get_user_model]' then get_user_model(). but only use these in models; you should use account.model.User anywhere else.
        null=True, # you have to use null=True since assigning user is difficult upon creation of this model. assign the author when creating an instance
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=100)
    cover_image = models.URLField(max_length=500, default="", blank=True)
    content = models.TextField(
        blank=True,
        # external_plugin_resources=[],
    ) # blank=True : not required column

    is_public = models.BooleanField(default=False)
    comment_amount = models.IntegerField(default=0)

    order = models.DecimalField(default=0, max_digits=5, decimal_places=3)
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ['-order', '-pk']

    @property
    def preview_content(self):
        return truncatechars(self.content, 100)


class Post(Document):
	tags = models.CharField(default="", blank=True, max_length=200)


class Comment(models.Model):
	content = models.TextField(blank=True)
	user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
    )
	created_at = models.DateTimeField(default=timezone.now)


class CaseStudy(Document):
	roles = models.CharField(default="", blank=True, max_length=500)
	time_spent = models.CharField(default="", blank=True, max_length=100)
	project_type = models.CharField(default="", blank=True, max_length=100)
	client_type = models.CharField(default="", blank=True, max_length=100)
	demonstrated_skills = models.CharField(default="", blank=True, max_length=500)

	class Meta:
		ordering = ['-order', '-pk']

	def __str__(self):
		return self.title


class HighlightedCaseStudy(models.Model):
    highlighted_abstract = models.TextField(default="", blank=True)

    highlighted_image = models.URLField(max_length=500, default="", blank=True)
    highlighted_image_css_position = models.CharField(max_length=10, default="", blank=True)
    highlighted_image_css_position_mobile = models.CharField(max_length=10, default="", blank=True)

    leader_words = models.TextField(default="", blank=True)
    leader_action = models.CharField(max_length=100)
    case_study = models.ForeignKey(CaseStudy, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['-case_study__order', '-pk']

    # @property
    # def user(self):
    # 	return self.case_study.user