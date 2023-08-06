import datetime

from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    FieldRowPanel,
    StreamFieldPanel,
    InlinePanel,
    PageChooserPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core import blocks
from wagtail.snippets.models import register_snippet
from wagtailgeowidget.blocks import GeoBlock, GeoAddressBlock
from modelcluster.fields import ParentalManyToManyField
from phonenumber_field.modelfields import PhoneNumberField

from goldbook.choices import DAY_CHOICES, CONTACT_TYPE_CHOICES, TASTING_ROOM_STYLE
from goldbook.util.helpers import my_year_validator


@register_snippet
class Occurrence(Orderable):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_("The name of the Occurrence as you'd like it to be seen by the public")
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        allow_unicode=True,
        max_length=255,
        help_text=_("The name of the region as it will appear in URLs e.g http://domain.com/wineries/northern-va/")
    )

    class Meta:
        verbose_name = 'Occurrence'
        verbose_name_plural = 'Occurrences'

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

@register_snippet
class WineTrail(Orderable):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_("The name of the Wine Trail as you'd like it to be seen by the public")
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        allow_unicode=True,
        max_length=255,
        help_text=_("The name of the Wine Trail  as it will appear in URLs e.g http://domain.com/wineries/pub-crawl/")
    )

    class Meta:
        verbose_name = 'Wine Trail'
        verbose_name_plural = 'Wine Trails'

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]


@register_snippet
class AVA(Orderable):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_("The name of the AVA as you'd like it to be seen by the public")
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        allow_unicode=True,
        max_length=255,
        help_text=_("The name of the AVA  as it will appear in URLs e.g http://domain.com/wineries/ava/blue-ridge/")
    )

    class Meta:
        verbose_name = 'AVA'
        verbose_name_plural = 'AVAs'

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]
# class OperatingHours(models.Model):
#     """
#     A Django model to capture operating hours for a Location
#     """
#
#     day = models.CharField(
#         max_length=4,
#         choices=DAY_CHOICES,
#         default='MON'
#     )
#     opening_time = models.TimeField(
#         blank=True,
#         null=True
#     )
#     closing_time = models.TimeField(
#         blank=True,
#         null=True
#     )
#     closed = models.BooleanField(
#         "Closed?",
#         blank=True,
#         help_text='Tick if location is closed on this day'
#     )
#
#     panels = [
#         FieldPanel('day'),
#         FieldPanel('opening_time'),
#         FieldPanel('closing_time'),
#         FieldPanel('closed'),
#     ]
#
#     class Meta:
#         abstract = True
#
#     def __str__(self):
#         if self.opening_time:
#             opening = self.opening_time.strftime('%H:%M')
#         else:
#             opening = '--'
#         if self.closing_time:
#             closed = self.closing_time.strftime('%H:%M')
#         else:
#             closed = '--'
#         return '{}: {} - {} {}'.format(
#             self.day,
#             opening,
#             closed,
#             settings.TIME_ZONE
#         )
#
#
# class WineryOperatingHours(Orderable, OperatingHours):
#     """
#     A model creating a relationship between the OperatingHours and Location
#     Note that unlike BlogPeopleRelationship we don't include a ForeignKey to
#     OperatingHours as we don't need that relationship (e.g. any Location open
#     a certain day of the week). The ParentalKey is the minimum required to
#     relate the two objects to one another. We use the ParentalKey's related_
#     name to access it from the LocationPage admin
#     """
#     location = ParentalKey(
#         'WineryOld',
#         related_name='hours_of_operation',
#         on_delete=models.CASCADE
#     )

@register_snippet
class WineryRegion(Orderable):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_("The name of the Region as you'd like it to be seen by the public")
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        allow_unicode=True,
        max_length=255,
        help_text=_("The name of the region as it will appear in URLs e.g http://domain.com/wineries/northern-va/")
    )

    class Meta:
        verbose_name = 'Winery Region'
        verbose_name_plural = 'Winery Regions'

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

@register_snippet
class ViewsFromSeating(Orderable):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        help_text=_("The name of the View as you'd like it to be seen by the public")
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        allow_unicode=True,
        max_length=255,
        help_text=_("The name of the view as it will appear in URLs e.g http://domain.com/wineries/northern-va/lakeviews/")
    )

    class Meta:
        verbose_name = 'View From Seating'
        verbose_name_plural = 'Seating Views'

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

class WineriesIndexPage(Page):
    template = 'goldbook/wineries_page.html'
    max_count = 1
    subpage_types = [
        'goldbook.Winery',  # appname.ModelName
    ]

    class Meta:
        verbose_name_plural = 'Wineries'
        verbose_name = 'Wineries'


class Winery(Page):
    subpage_types = []
    description = RichTextField(null=True, blank=True)
    notes = RichTextField(null=True, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True, verbose_name='Business Phone')
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name='Business Email')
    year_established = models.IntegerField(validators=[my_year_validator], blank=True, null=True,
                                           verbose_name='Year established')
    number_of_wines = models.IntegerField(blank=True, null=True, verbose_name='Number of Wines Produced')
    total_number_wine_cases_annually = models.IntegerField(blank=True, null=True,
                                                           verbose_name='Total number of cases in production annually')
    number_of_acres_under_vine = models.IntegerField(blank=True, null=True, verbose_name='Number of acres under vine')
    winery_region = models.ForeignKey('goldbook.WineryRegion', null=True, blank=True, on_delete=models.SET_NULL,
                                      verbose_name='Region of VA', related_name='+')
    ava =  models.ForeignKey('goldbook.AVA', blank=True, null=True,  on_delete=models.SET_NULL,
                                      verbose_name='AVA', related_name='+')
    trail_a_part_of = ParentalManyToManyField("goldbook.WineTrail", blank=True, verbose_name='Trail a part of')
    largest_town_within_30_mins = models.CharField(max_length=254, blank=True, null=True,
                                                   verbose_name='Largest town within 30 min')
    tasting_room_within_vineyard = models.BooleanField(blank=True, null=True,
                                                       verbose_name='Is the Tasting Room located within a vineyard?')
    wine_tours_available = models.BooleanField(blank=True, null=True, verbose_name='Winery tours available?')
    wines_sold_online = models.BooleanField(blank=True, null=True, verbose_name='Wines sold online?')
    wine_club = models.BooleanField(blank=True, null=True, verbose_name='Wines Club?')
    num_wine_club_members = models.IntegerField(blank=True, null=True, verbose_name='Number of Wine Club members?')
    num_gov_cup_medals = models.IntegerField(blank=True, null=True,
                                             verbose_name='Number of Gov Cup Gold medals over the years?')
    num_other_medals = models.IntegerField(blank=True, null=True, verbose_name='Number of other gold medals of note')

    primary_contact_name = models.CharField(max_length=254, blank=True, null=True, verbose_name='Primary Contact Name')
    primary_contact_title = models.CharField(max_length=254, blank=True, null=True,
                                             verbose_name='Primary Contact Title')
    primary_contact_phone = models.CharField(max_length=254, blank=True, null=True,
                                             verbose_name='Primary Contact Phone')
    primary_contact_email = models.CharField(max_length=254, blank=True, null=True,
                                             verbose_name='Primary Contact email')
    secondary_contact_name = models.CharField(max_length=254, blank=True, null=True,
                                              verbose_name='Secondary Contact Name')
    secondary_contact_title = models.CharField(max_length=254, blank=True, null=True,
                                               verbose_name='Secondary Contact Title')
    secondary_contact_phone = models.CharField(max_length=254, blank=True, null=True,
                                               verbose_name='Secondary Contact Phone')
    secondary_contact_email = models.CharField(max_length=254, blank=True, null=True,
                                               verbose_name='Secondary Contact email')
    owner_name = models.CharField(max_length=254, blank=True, null=True,
                                  verbose_name='Owner Name')
    owner_phone = models.CharField(max_length=254, blank=True, null=True,
                                   verbose_name='Owner Phone')
    owner_email = models.CharField(max_length=254, blank=True, null=True,
                                   verbose_name='Owner email')
    owner_bio = RichTextField(null=True, blank=True, verbose_name='Owner Bio')
    winemaker_name = models.CharField(max_length=254, blank=True, null=True,
                                      verbose_name='Winemaker Name')
    winemaker_phone = models.CharField(max_length=254, blank=True, null=True,
                                       verbose_name='Winemaker Phone')
    winemaker_email = models.CharField(max_length=254, blank=True, null=True,
                                       verbose_name='Winemaker email')
    winemaker_bio = RichTextField(null=True, blank=True, verbose_name='Winemaker Bio')
    brewery = models.BooleanField(blank=True, null=True, verbose_name='Brewery?')
    veg_garden = models.BooleanField(blank=True, null=True, verbose_name='Vegetable or fruit garden on premise?')
    flower_garden = models.BooleanField(blank=True, null=True, verbose_name='Formal or flower garden on premise?')
    bee_apiary = models.BooleanField(blank=True, null=True, verbose_name='Bee apiary on premise?')
    sheep = models.BooleanField(blank=True, null=True, verbose_name='Sheep on premise?')
    goats = models.BooleanField(blank=True, null=True, verbose_name='Goats on premise?')
    chicken = models.BooleanField(blank=True, null=True, verbose_name='Chickens on premise?')
    cattle = models.BooleanField(blank=True, null=True, verbose_name='Cattle on premise?')
    horses = models.BooleanField(blank=True, null=True, verbose_name='Horses on premise?')
    honey = models.BooleanField(blank=True, null=True, verbose_name='honey?')
    jelly = models.BooleanField(blank=True, null=True, verbose_name='jelly?')
    cheese = models.BooleanField(blank=True, null=True, verbose_name='cheese?')
    chocolate = models.BooleanField(blank=True, null=True, verbose_name='chocolate?')
    other_production = models.CharField(max_length=254, blank=True, null=True,
                                        verbose_name='Other?')
    unique_feature_or_activity = RichTextField(blank=True, null=True,
                                               verbose_name='Uniquely different property feature or activity of note?')

    fridge_nibbles = models.BooleanField(blank=True, null=True, verbose_name='Refrigerated nibbles?')
    counter_service_casual_fare = models.BooleanField(blank=True, null=True,
                                                      verbose_name='Counter service casual fare?')
    table_service_restaurant = models.BooleanField(blank=True, null=True, verbose_name='Table service restaurant?')
    fine_dining = models.BooleanField(blank=True, null=True, verbose_name='Fine dining?')
    outside_picnic_food_welcome = models.BooleanField(blank=True, null=True,
                                                      verbose_name='Outside picnic food welcome?')
    tasting_room_style = models.CharField(max_length=20, choices=TASTING_ROOM_STYLE, null=True, default=None,
                                          blank=True)
    seating_capacity = models.IntegerField(blank=True, null=True, verbose_name='Seating Capacity')
    reservations_available = models.BooleanField(blank=True, null=True, verbose_name='Reservations available?')
    walk_in_limit = models.BooleanField(blank=True, null=True, verbose_name='Quantity limit on walk-in party size?')
    quantity_limit_on_walkin_party_size = models.CharField(max_length=254, blank=True, null=True, verbose_name='Quantity limit on walk-in party size?')
    dogs_welcome = models.BooleanField(blank=True, null=True, verbose_name='Dogs welcome?')
    children_welcome = models.BooleanField(blank=True, null=True, verbose_name='Children welcome?')
    tastingroom_views  = ParentalManyToManyField("goldbook.ViewsFromSeating", blank=True, verbose_name='Views from Tasting Room seating?')
    tasting_room_views = models.BooleanField(blank=True, null=True, verbose_name='Views from Tasting Room seating?')
    tasting_room_views_mountains = models.BooleanField(blank=True, null=True, verbose_name='Mountains?')
    tasting_room_views_vineyard = models.BooleanField(blank=True, null=True, verbose_name='Vineyard?')
    tasting_room_views_countryside = models.BooleanField(blank=True, null=True, verbose_name='Countryside?')
    tasting_room_views_urban = models.BooleanField(blank=True, null=True, verbose_name='Urban Views?')
    fireplace = models.BooleanField(blank=True, null=True, verbose_name='Fireplace present?')
    fire_tables = models.BooleanField(blank=True, null=True, verbose_name='Firetables available?')
    outdoor_heating = models.BooleanField(blank=True, null=True, verbose_name='Outdoor heating available?')
    shade = models.BooleanField(blank=True, null=True,
                                verbose_name='Is shade abundantly available via umbrellas, porches, pergolas?')
    lawn = models.BooleanField(blank=True, null=True, verbose_name='Is there a lawn available for picnics and games?')
    live_music = ParentalManyToManyField("goldbook.Occurrence", blank=True, verbose_name='Live Music?')
    food_truck = ParentalManyToManyField("goldbook.Occurrence", blank=True, verbose_name='Food Truck Available?', related_name='food_truck')
    loging = models.BooleanField(blank=True, null=True, verbose_name='Lodging on premise?')
    souvenirs = models.BooleanField(blank=True, null=True, verbose_name='Souvenir shopping on premise?')
    festivals = models.BooleanField(blank=True, null=True, verbose_name='Festivals?')
    festivals_info = models.TextField(blank=True, null=True, verbose_name='Festivals titles and months')
    dinner_events = models.BooleanField(blank=True, null=True, verbose_name='Dinner events?')
    dinner_events_info = models.TextField(blank=True, null=True, verbose_name='Dinner event titles & months')
    classes_or_workshops = models.BooleanField(blank=True, null=True, verbose_name='Classes or workshops?')
    classes_or_workshops_info = models.TextField(blank=True, null=True,
                                                 verbose_name='Classes or workshops titles & months')
    corporate_events = models.BooleanField(blank=True, null=True, verbose_name='Corporate events?')
    private_party_events = models.BooleanField(blank=True, null=True, verbose_name='Private party events?')
    minimum_private_party_resv = models.IntegerField(blank=True, null=True,
                                                     verbose_name='Minimum required for private party reservations')
    maximum_private_party_resv = models.IntegerField(blank=True, null=True,
                                                     verbose_name='Maximum required for private party reservations')
    wedding_events = models.BooleanField(blank=True, null=True, verbose_name='Weddings?')
    wedding_event_capacity = models.IntegerField(blank=True, null=True, verbose_name='Wedding capacity')
    wedding_event_avg_per_year = models.IntegerField(blank=True, null=True,
                                                     verbose_name='Average number of wedding per year')
    wedding_event_price_range = models.CharField(max_length=254, blank=True, null=True,
                                                 verbose_name='Average price range of weddings hosted')
    winery_catering_available = models.BooleanField(blank=True, null=True,
                                                    verbose_name='Winery provided catering available?')
    winery_catering_required = models.BooleanField(blank=True, null=True,
                                                   verbose_name='Winery provided catering Required?')
    designated_ceremony_site = models.BooleanField(blank=True, null=True, verbose_name='Designated ceremony site?')
    ceremony_views  = ParentalManyToManyField("goldbook.ViewsFromSeating", blank=True, verbose_name='Views from Ceremony?', related_name='ceremony_views')

    ceremony_views_mountain = models.BooleanField(blank=True, null=True, verbose_name='Ceremony Mountain Views')
    ceremony_views_vineyard = models.BooleanField(blank=True, null=True, verbose_name='Ceremony Vineyard Views')
    ceremony_views_countryside = models.BooleanField(blank=True, null=True, verbose_name='Ceremony Countryside Views')
    ceremony_views_urban = models.BooleanField(blank=True, null=True, verbose_name='Ceremony Urban Views')
    designated_reception_hall = models.BooleanField(blank=True, null=True, verbose_name='Designated Reception Hall?')
    designated_reception_hall_views  = ParentalManyToManyField("goldbook.ViewsFromSeating", blank=True, verbose_name='Views from Reception Hall?', related_name='reception_hall_views')

    designated_reception_hall_views_mountain = models.BooleanField(blank=True, null=True,
                                                                   verbose_name='Designated Reception Hall Mountain Views')
    designated_reception_hall_views_vineyard = models.BooleanField(blank=True, null=True,
                                                                   verbose_name='Designated Reception Hall Vineyard Views')
    designated_reception_hall_views_countryside = models.BooleanField(blank=True, null=True,
                                                                      verbose_name='Designated Reception Hall Countryside Views')
    designated_reception_hall_views_urban = models.BooleanField(blank=True, null=True,
                                                                verbose_name='Designated Reception Hall Urban Views')
    familiar_with_wc_life = models.BooleanField(blank=True, null=True,
                                                verbose_name='Are you familiar with Wine & Country Life?')
    display_wc_life_tasting_room = models.BooleanField(blank=True, null=True,
                                                       verbose_name='Do you display it in the Tasting Room?')
    wc_life_advertiser = models.BooleanField(blank=True, null=True,
                                             verbose_name='Do you currently advertise in WC.Life?')
    familiar_with_wc_weddings = models.BooleanField(blank=True, null=True,
                                                    verbose_name='Are you familiar with Wine & Country Weddings?')
    display_wc_weddings_tasting_room = models.BooleanField(blank=True, null=True,
                                                           verbose_name='Do you display it in the Tasting Room?')
    wc_weddings_advertiser = models.BooleanField(blank=True, null=True,
                                                 verbose_name='Do you currently advertise in WC.Weddings?')
    familiar_with_wc_goldbook = models.BooleanField(blank=True, null=True,
                                                    verbose_name='Are you familiar with The Wine & Country Gold Book?')
    sell_wc_goldbook = models.BooleanField(blank=True, null=True,
                                           verbose_name='Do they currently sell copies of the Gold Book?')
    wc_goldbook_advertiser = models.BooleanField(blank=True, null=True,
                                                 verbose_name='Do they currently advertise in WC.Gold Book?')

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='winery_logo'
    )
    address = StreamField([
        ('map_struct', blocks.StructBlock([
            ('address', GeoAddressBlock(required=True)),
            ('map', GeoBlock(address_field='address')),
        ]))

    ], blank=True)

    address.verbose_name = 'Main Address'

    tasting_room_address = StreamField([
        ('map_struct', blocks.StructBlock([
            ('address', GeoAddressBlock(required=False)),
            ('map', GeoBlock(address_field='tasting_room_address')),
        ], ),)

    ], blank=True)
    tasting_room_address.verbose_name = 'Tasting Room Address (if different)'

    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('description'),
    ]

    # Editor panels configuration

    page_content_panels = Page.content_panels

    contact_info_panels = [

        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('primary_contact_name'),
                    FieldPanel('primary_contact_title'),
                ]),
                FieldRowPanel([
                    FieldPanel('primary_contact_phone'),
                    FieldPanel('primary_contact_email'),
                ]),
            ],
            heading="Primary Contact Info",
        ),

        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('secondary_contact_name'),
                    FieldPanel('secondary_contact_title'),
                ]),
                FieldRowPanel([
                    FieldPanel('secondary_contact_phone'),
                    FieldPanel('secondary_contact_email'),
                ]),
            ],
            heading="Secondary Contact Info",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('owner_name'),
                    FieldPanel('owner_phone'),
                    FieldPanel('owner_email'),
                ]),
                FieldRowPanel([
                    FieldPanel('owner_bio'),
                ]),
                FieldRowPanel([
                    FieldPanel('winemaker_name'),
                    FieldPanel('winemaker_phone'),
                    FieldPanel('winemaker_email'),
                ]),
                FieldRowPanel([
                    FieldPanel('winemaker_bio'),
                ]),
            ],
            heading="Owner and Winemaker Info",
        ),

    ]

    address_panels = [
        MultiFieldPanel(
            [
                FieldPanel('phone_number'),
                FieldPanel('email'),
            ],
            heading="Main Phone and Email Address",
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('address'),
            ],
            heading="Address",
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('tasting_room_address'),
            ],
            heading="Tasting Room Address (if different)",
        ),

    ]
    media_panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel('logo'),
            ],
            heading="Media",
        ),
    ]

    description_panels = [
        FieldPanel('description', classname="full"),

    ]

    winery_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('year_established'),
                    FieldPanel('number_of_wines'),
                ]),
                FieldRowPanel([
                    FieldPanel('total_number_wine_cases_annually'),
                    FieldPanel('number_of_acres_under_vine'),
                ]),
                FieldRowPanel([
                    FieldPanel('ava'),
                ]),
                FieldRowPanel([
                    FieldPanel('winery_region'),
                    FieldPanel('tasting_room_within_vineyard'),
                ]),
                # FieldRowPanel([
                #     FieldPanel('trail_a_part_of', widget=forms.CheckboxSelectMultiple)
                # ]),

                FieldRowPanel([
                    FieldPanel('wine_tours_available'),
                    FieldPanel('wines_sold_online'),
                ]),
                FieldRowPanel([
                    FieldPanel('wine_club'),
                    FieldPanel('num_wine_club_members'),
                ]),
                FieldRowPanel([
                    FieldPanel('num_gov_cup_medals'),
                    FieldPanel('num_other_medals'),
                ]),
            ],
            heading="Winery Info",
        ),
    ]

    production_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('brewery'),
                    FieldPanel('veg_garden'),
                    FieldPanel('flower_garden'),
                ]),
                FieldRowPanel([
                    FieldPanel('bee_apiary'),
                    FieldPanel('sheep'),
                    FieldPanel('goats'),
                ]),
                FieldRowPanel([
                    FieldPanel('chicken'),
                    FieldPanel('cattle'),
                    FieldPanel('horses'),
                ]),
                FieldRowPanel([
                    FieldPanel('honey'),
                    FieldPanel('jelly'),
                    FieldPanel('cheese'),
                ]),
                FieldRowPanel([
                    FieldPanel('chocolate'),
                    FieldPanel('other_production'),
                ]),
                FieldRowPanel([
                    FieldPanel('unique_feature_or_activity'),
                ]),
            ],
            heading="Other Production",
        ),
    ]

    food_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('fridge_nibbles'),
                    FieldPanel('counter_service_casual_fare'),
                    FieldPanel('table_service_restaurant'),
                ]),
                FieldRowPanel([
                    FieldPanel('fine_dining'),
                    FieldPanel('outside_picnic_food_welcome'),
                ]),
                FieldRowPanel([
                    FieldPanel('food_truck', widget=forms.CheckboxSelectMultiple),
                ]),
            ],
            heading="Food",
        ),
    ]

    tasting_room_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('tasting_room_style'),
                    FieldPanel('seating_capacity'),
                    FieldPanel('reservations_available'),

                ]),
                FieldRowPanel([
                    FieldPanel('quantity_limit_on_walkin_party_size'),
                    FieldPanel('dogs_welcome'),
                    FieldPanel('children_welcome'),

                ]),
                FieldRowPanel([
                    FieldPanel('tastingroom_views', widget=forms.CheckboxSelectMultiple),

                ]),

                FieldRowPanel([
                    FieldPanel('fireplace'),
                    FieldPanel('fire_tables'),
                    FieldPanel('outdoor_heating'),
                ]),
                FieldRowPanel([
                    FieldPanel('shade'),
                    FieldPanel('lawn'),
                ]),
                FieldRowPanel([
                    FieldPanel("live_music", widget=forms.CheckboxSelectMultiple)
                ]),
                FieldRowPanel([
                    FieldPanel('loging'),
                    FieldPanel('souvenirs'),
                ]),
                FieldRowPanel([
                    FieldPanel('festivals'),
                    FieldPanel('festivals_info'),
                ]),
                FieldRowPanel([
                    FieldPanel('dinner_events'),
                    FieldPanel('dinner_events_info'),
                ]),
                FieldRowPanel([
                    FieldPanel('classes_or_workshops'),
                    FieldPanel('classes_or_workshops_info'),
                ]),
            ],
            heading="Tasting Room Experience",
        ),
    ]

    event_services_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('corporate_events'),
                    FieldPanel('private_party_events'),

                ]),
                FieldRowPanel([
                    FieldPanel('minimum_private_party_resv'),
                    FieldPanel('maximum_private_party_resv'),

                ]),
                FieldRowPanel([
                    FieldPanel('wedding_events'),
                    FieldPanel('wedding_event_capacity'),

                ]),
                FieldRowPanel([
                    FieldPanel('wedding_event_avg_per_year'),
                    FieldPanel('wedding_event_price_range'),

                ]),
                FieldRowPanel([
                    FieldPanel('winery_catering_available'),
                    FieldPanel('winery_catering_required'),
                ]),
                FieldRowPanel([
                    FieldPanel('designated_ceremony_site'),
                ]),
                FieldRowPanel([
                    FieldPanel('ceremony_views', widget=forms.CheckboxSelectMultiple),

                ]),

                FieldRowPanel([
                    FieldPanel('designated_reception_hall'),
                ]),
                FieldRowPanel([
                    FieldPanel('designated_reception_hall_views', widget=forms.CheckboxSelectMultiple),

                ]),

            ],
            heading="Event Services",
        ),
    ]

    advertising_info_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('familiar_with_wc_life'),
                    FieldPanel('display_wc_life_tasting_room'),
                    FieldPanel('wc_life_advertiser'),

                ]),
                FieldRowPanel([
                    FieldPanel('familiar_with_wc_weddings'),
                    FieldPanel('display_wc_weddings_tasting_room'),
                    FieldPanel('wc_weddings_advertiser'),
                ]),
                FieldRowPanel([
                    FieldPanel('familiar_with_wc_goldbook'),
                    FieldPanel('sell_wc_goldbook'),
                    FieldPanel('wc_goldbook_advertiser'),
                ]),
            ],
            heading="Advertising Info",
        ),
    ]

    notes_panels = [
        MultiFieldPanel(
            [
                FieldPanel('notes'),
            ],
            heading="Notes",
        ),
    ]

    combined_info_panels = Page.content_panels + \
                           contact_info_panels + \
                           address_panels + \
                           winery_panels + \
                           production_panels + \
                           food_panels + \
                           tasting_room_panels + \
                           event_services_panels + \
                           advertising_info_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(combined_info_panels, heading='Information/Questionaire'),
            # This is our custom banner_panels. It's just a list, how easy!
            # ObjectList(page_content_panels, heading="Basic Info"),
            # ObjectList(contact_info_panels, heading="Contact Info"),
            # ObjectList(address_panels, heading="Address/Phone/Email"),
            # ObjectList(winery_panels, heading="Winery Info"),
            # ObjectList(production_panels, heading="Other Production"),
            # ObjectList(food_panels, heading="Food"),
            # ObjectList(tasting_room_panels, heading="Tasting Room Experience"),
            # ObjectList(event_services_panels, heading="Event Services"),
            # ObjectList(advertising_info_panels, heading="Advertising Info"),
            # ObjectList(media_panels, heading="Media"),
            # ObjectList(notes_panels, heading="Notes"),
            # ObjectList(Page.promote_panels, heading='Promotional Stuff'),
            # ObjectList(Page.settings_panels, heading='Settings Stuff'),
        ]
    )


Winery._meta.get_field("title").verbose_name = "Winery Name"
