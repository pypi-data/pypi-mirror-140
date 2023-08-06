import logging

from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from cacheops import invalidate_obj

from ..custom_model_form import CustomModelForm
from ..custom_tree_node_form import CustomTreeNodeForm
from ...models import Language, LanguageTreeNode


logger = logging.getLogger(__name__)


class LanguageTreeNodeForm(CustomModelForm, CustomTreeNodeForm):
    """
    Form for creating and modifying language tree node objects
    """

    parent = forms.ModelChoiceField(
        queryset=LanguageTreeNode.objects.all(),
        required=False,
        label=capfirst(LanguageTreeNode._meta.get_field("parent").verbose_name),
    )

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        #: The model of this :class:`django.forms.ModelForm`
        model = LanguageTreeNode
        #: The fields of the model which should be handled by this form
        fields = ["language", "visible", "active"]

    def __init__(self, **kwargs):
        r"""
        Initialize language tree node form

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict
        """

        if "data" in kwargs:
            # Copy QueryDict because it is immutable
            data = kwargs.pop("data").copy()
            # Use the parent node as value for the ref node
            data["_ref_node_id"] = data["parent"]
            data["_position"] = "first-child"
            # Set the kwargs to updated POST data again
            kwargs["data"] = data

        # Instantiate CustomModelForm
        super().__init__(**kwargs)

        parent_queryset = self.instance.region.language_tree_nodes

        if self.instance.id:
            descendant_ids = [
                descendant.id
                for descendant in self.instance.get_cached_descendants(
                    include_self=True
                )
            ]
            parent_queryset = parent_queryset.exclude(id__in=descendant_ids)
            self.fields["parent"].initial = self.instance.parent_id
            excluded_languages = [
                language.id
                for language in self.instance.region.languages
                if language != self.instance.language
            ]
        else:
            excluded_languages = [
                language.id for language in self.instance.region.languages
            ]

        # limit possible parents to nodes of current region
        self.fields["parent"].queryset = parent_queryset
        self.fields["_ref_node_id"].choices = self.fields["parent"].choices
        # limit possible languages to those which are not yet included in the tree
        self.fields["language"].queryset = Language.objects.exclude(
            id__in=excluded_languages
        )

    def clean(self):
        """
        Validate form fields which depend on each other, see :meth:`django.forms.Form.clean`:
        Don't allow multiple root nodes for one region:
        If self is a root node and the region already has a default language, raise a
        :class:`~django.core.exceptions.ValidationError`.

        :return: The cleaned form data
        :rtype: dict
        """
        cleaned_data = super().clean()
        default_language = self.instance.region.default_language
        # There are two cases in which this error is thrown.
        # Both cases include that the parent field is None.
        # 1. The instance does exist:
        #   - The default language is different from the instance language
        # 2. The instance does not exist:
        #   - The default language exists
        if not cleaned_data.get("parent") and (
            (self.instance.id and default_language != self.instance.language)
            or (not self.instance.id and default_language)
        ):
            self.add_error(
                "parent",
                forms.ValidationError(
                    _(
                        "This region has already a default language."
                        "Please specify a source language for this language."
                    ),
                    code="invalid",
                ),
            )
        logger.debug(
            "LanguageTreeNodeForm validated [2] with cleaned data %r", cleaned_data
        )
        return cleaned_data

    def save(self, commit=True):
        """
        This method extends the default ``save()``-method of the base :class:`~django.forms.ModelForm` to flush
        the cache after commiting.

        :param commit: Whether or not the changes should be written to the database
        :type commit: bool

        :return: The saved page translation object
        :rtype: ~integreat_cms.cms.models.pages.page_translation.PageTranslation
        """
        # Save CustomModelForm and flush Cache
        result = super().save(commit=commit)

        for page in self.instance.region.pages.all():
            invalidate_obj(page)
        for poi in self.instance.region.pois.all():
            invalidate_obj(poi)
        for event in self.instance.region.events.all():
            invalidate_obj(event)
        return result
