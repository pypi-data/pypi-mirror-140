import logging

from django import forms
from django.conf import settings
from django.utils.translation import override, ugettext_lazy as _
from django.apps import apps

from ....gvz_api.utils import GvzRegion
from ...models import Region, PageTranslation, LanguageTreeNode
from ...utils.matomo_api_manager import MatomoException
from ...utils.slug_utils import generate_unique_slug_helper
from ...utils.translation_utils import ugettext_many_lazy as __
from ..icon_widget import IconWidget
from ..custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class RegionForm(CustomModelForm):
    """
    Form for creating and modifying region objects
    """

    duplicated_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        empty_label=_("Do no import initial content"),
        required=False,
    )

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        #: The model of this :class:`django.forms.ModelForm`
        model = Region
        #: The fields of the model which should be handled by this form
        fields = [
            "name",
            "common_id",
            "slug",
            "events_enabled",
            "chat_enabled",
            "push_notifications_enabled",
            "latitude",
            "longitude",
            "postal_code",
            "admin_mail",
            "statistics_enabled",
            "matomo_id",
            "matomo_token",
            "status",
            "page_permissions_enabled",
            "administrative_division",
            "aliases",
            "icon",
            "administrative_division_included",
            "offers",
            "short_urls_enabled",
            "custom_prefix",
        ]
        #: The widgets which are used in this form
        widgets = {
            "icon": IconWidget(),
            "offers": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        r"""
        Initialize region form

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict
        """
        super().__init__(*args, **kwargs)

        self.fields["slug"].required = False

    def save(self, commit=True):
        """
        This method extends the default ``save()``-method of the base :class:`~django.forms.ModelForm` to set attributes
        which are not directly determined by input fields.

        :param commit: Whether or not the changes should be written to the database
        :type commit: bool

        :return: The saved region object
        :rtype: ~integreat_cms.cms.models.regions.region.Region
        """

        # Only duplicate content if region is created and a region was selected
        duplicate_region = (
            not self.instance.id and self.cleaned_data["duplicated_region"]
        )

        # Save CustomModelForm
        region = super().save(commit=commit)

        if duplicate_region:
            source_region = self.cleaned_data["duplicated_region"]
            logger.info("Duplicate content of %r to %r", source_region, region)
            # Duplicate language tree
            duplicate_language_tree(source_region, region)
            # Duplicate pages
            duplicate_pages(source_region, region)
            # Duplicate media content
            duplicate_media(source_region, region)

        return region

    def clean(self):
        """
        Validate form fields which depend on each other, see :meth:`django.forms.Form.clean`

        :return: The cleaned form data
        :rtype: dict
        """
        cleaned_data = super().clean()
        # Check wether statistics can be enabled
        if cleaned_data["statistics_enabled"] and not cleaned_data["matomo_token"]:
            self.add_error(
                "statistics_enabled",
                _(
                    "Statistics can only be enabled when a valid access token is supplied."
                ),
            )
        # Automatically set the Matomo ID
        if cleaned_data["matomo_token"]:
            try:
                cleaned_data["matomo_id"] = self.instance.statistics.get_matomo_id(
                    token_auth=cleaned_data["matomo_token"]
                )
            except MatomoException as e:
                logger.exception(e)
                self.add_error(
                    "matomo_token", _("The provided access token is invalid.")
                )
        else:
            cleaned_data["matomo_id"] = None

        # Get additional data from GVZ API
        if apps.get_app_config("gvz_api").api_available:
            gvz_region = GvzRegion(
                region_name=cleaned_data["name"],
                region_ags=cleaned_data["common_id"],
                region_type=cleaned_data["administrative_division"],
            )
            if gvz_region.aliases and cleaned_data["aliases"] in [{}, ""]:
                cleaned_data["aliases"] = gvz_region.aliases
            if gvz_region.longitude and cleaned_data["longitude"] == 0.0:
                cleaned_data["longitude"] = gvz_region.longitude
            if gvz_region.latitude and cleaned_data["latitude"] == 0.0:
                cleaned_data["latitude"] = gvz_region.latitude

        logger.debug("RegionForm validated [2] with cleaned data %r", cleaned_data)
        return cleaned_data

    def clean_slug(self):
        """
        Validate the slug field (see :ref:`overriding-modelform-clean-method`)

        :return: A unique slug based on the input value
        :rtype: str
        """
        return generate_unique_slug_helper(self, "region")

    def clean_custom_prefix(self):
        """
        Validate the custom prefix field. (see :ref:`overriding-modelform-clean-method`)

        :return: The given prefix or ``None`` if it is invalid
        :rtype: str
        """
        cleaned_data = self.cleaned_data
        # Validate custom prefix
        if cleaned_data.get("custom_prefix"):
            # Get the administrative divisions as conflicting options
            administrative_divisions = [
                label
                for choice, label in self.fields["administrative_division"].choices
            ]
            for language_slug, language_name in settings.LANGUAGES:
                # Check if at least one translation of the labels matches the prefix
                with override(language_slug):
                    # Force evaluation of lazy-translated text
                    translated_administrative_divisions = list(
                        map(str, administrative_divisions)
                    )
                # Check if custom prefix could also be set via the administrative division
                if (
                    cleaned_data.get("custom_prefix")
                    in translated_administrative_divisions
                ):
                    error_messages = []
                    # Get currently selected administrative division
                    selected_administrative_division = dict(
                        self.fields["administrative_division"].choices
                    )[cleaned_data.get("administrative_division")]
                    # Check if administrative division needs to be changed to translated version
                    if cleaned_data.get("custom_prefix") in administrative_divisions:
                        desired_administrative_division = cleaned_data.get(
                            "custom_prefix"
                        )
                    else:
                        # Get index of translated administrative division
                        index = translated_administrative_divisions.index(
                            cleaned_data.get("custom_prefix")
                        )
                        # Get original label which needs to be selected in list
                        desired_administrative_division = administrative_divisions[
                            index
                        ]
                    if (
                        selected_administrative_division
                        == desired_administrative_division
                    ):
                        error_messages.append(
                            _(
                                "'{}' is already selected as administrative division."
                            ).format(selected_administrative_division)
                        )
                    else:
                        error_messages.append(
                            _("Please select '{}' as administrative division.").format(
                                desired_administrative_division
                            )
                        )
                    # Check if default language needs to be changed in order to use this administrative division
                    if (
                        not self.instance.default_language
                        or self.instance.default_language.native_name != language_name
                    ):
                        error_messages.append(
                            _(
                                "Please set {} as default language for this region."
                            ).format(_(language_name))
                        )
                    # Check if administrative division is included in name yet
                    if not cleaned_data.get("administrative_division_included"):
                        error_messages.append(
                            _("Please enable '{}'.").format(
                                self.fields["administrative_division_included"].label
                            )
                        )
                    self.add_error(
                        "custom_prefix",
                        __(*error_messages),
                    )
        # Check if administrative division is also included in the name and allow only one of both prefix options
        if cleaned_data.get("custom_prefix") and cleaned_data.get(
            "administrative_division_included"
        ):
            self.add_error(
                "custom_prefix",
                _(
                    "You cannot include the administrative division into the name and use a custom prefix at the same time."
                ),
            )
        return cleaned_data.get("custom_prefix")


def duplicate_language_tree(
    source_region, target_region, source_parent_id=None, target_parent=None
):
    """
    Function to duplicate the language tree of one region to another.

    Usage: duplicate_language_tree(source_region, target_region)

    This is a recursive function to walk the whole language tree. It starts at root level with the default parent None.
    The recursion is necessary because the new nodes need their correct (also duplicated) parent node.

    :param source_region: The region from which the language tree should be duplicated
    :type source_region: cms.models.regions.region.Region

    :param target_region: The region to which the language tree should be added
    :type target_region: cms.models.regions.region.Region

    :param source_parent_id: The current parent node id of the recursion
    :type source_parent_id: int

    :param target_parent: The node of the target region which is the duplicate of the source parent node
    :type target_parent: cms.models.pages.page.Page
    """

    # Iterate over all children of the current source parent, beginning with the root node
    for node in LanguageTreeNode.objects.filter(
        region=source_region, parent__id=source_parent_id
    ).all():
        # Store the source node id for the next iteration
        source_node_id = node.pk
        # Change the region and parent to its new values
        node.region = target_region
        node.parent = target_parent
        # Delete the primary key to force an insert
        node.pk = None
        # Check if the resulting node is valid
        node.full_clean()
        # Save the duplicated node
        node.save()
        # Call the function recursively for all children of the current node
        duplicate_language_tree(source_region, target_region, source_node_id, node)


def duplicate_pages(
    source_region, target_region, source_parent_id=None, target_parent=None, level=0
):
    """
    Function to duplicate all pages of one region to another.

    Usage: duplicate_pages(source_region, target_region)

    This is a recursive function to walk the whole page tree. It starts at root level with the default parent None.
    The recursion is necessary because the new pages need their correct (also duplicated) parent page.

    :param source_region: The region from which the pages should be duplicated
    :type source_region: cms.models.regions.region.Region

    :param target_region: The region to which the pages should be added
    :type target_region: cms.models.regions.region.Region

    :param source_parent_id: The current parent page id of the recursion
    :type source_parent_id: int

    :param target_parent: The page of the target region which is the duplicate of the source parent page
    :type target_parent: cms.models.pages.page.Page

    :param level: recursion level to get a pretty log output
    :type level: int
    """

    logger.debug(
        "%s Source parent %r started (target parent %r)",
        "|  " * level + "├" + "─",
        source_parent_id,
        target_parent,
    )

    # At first, get all pages from the source region with a specific parent page
    # As the parent will be None for the initial call, this returns all pages from the root level
    for target_page in source_region.pages.filter(parent__id=source_parent_id):
        logger.debug(
            "%s Source page %r started", "|  " * (level + 1) + "├" + "─", target_page
        )
        # Store the source page id into a buffer (if we store the whole object instance instead of only the id,
        # it will also change when we change target_page, because both variables would reference the same object)
        source_page_id = target_page.pk
        # Set the parent of the new page to the previously created target parent
        target_page.parent = target_parent
        # Set the region of the new page to the target region
        target_page.region = target_region
        # Delete the primary key to duplicate the object instance instead of updating it
        target_page.pk = None
        # Check if the page is valid
        target_page.full_clean()
        # Save duplicated page
        target_page.save()
        # Clone all page translations of the source page
        for page_translation in PageTranslation.objects.filter(page__id=source_page_id):
            # Set the page of the source translation to the new page
            page_translation.page = target_page
            # Delete the primary key to duplicate the object instance instead of updating it
            page_translation.pk = None
            # Check if the page translation is valid
            page_translation.full_clean()
            # Save duplicated page translation
            page_translation.save()
            logger.debug(
                "%s %r finished",
                "|  " * (level + 3) + "├" + "─",
                page_translation,
            )
        # Recursively call this function with the current pages as new parents
        duplicate_pages(
            source_region, target_region, source_page_id, target_page, level + 2
        )
        logger.debug(
            "%s Source page %r finished (target %r)",
            "|  " * (level + 1) + "├" + "─",
            source_page_id,
            target_page,
        )
    logger.debug(
        "%s Source parent %r finished (target parent %r)",
        "|  " * level + "├" + "─",
        source_parent_id,
        target_parent,
    )


# pylint: disable=unused-argument
def duplicate_media(source_region, target_region):
    """
    Function to duplicate all media of one region to another.

    :param source_region: the source region from which the pages should be duplicated
    :type source_region: ~integreat_cms.cms.models.regions.region.Region

    :param target_region: the target region
    :type target_region: ~integreat_cms.cms.models.regions.region.Region

    """
    # TODO: implement duplication of all media files
