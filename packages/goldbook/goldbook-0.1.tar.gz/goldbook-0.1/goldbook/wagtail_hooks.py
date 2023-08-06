from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.core import hooks
from wagtail.admin.widgets import Button, PageListingButton

@hooks.register('construct_page_listing_buttons')
def replace_page_listing_button_item(buttons, page, page_perms, is_parent=False, context=None):
    for index, button in enumerate(buttons):
       # basic code only - recommend you find a more robust way to confirm this is the add child page button
        if button.label == 'Add child page':
            button.label = 'Add New Winery'
            buttons[index] = button # update the matched button with a new one (note. PageListingButton is used in page listing)
