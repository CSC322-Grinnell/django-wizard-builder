from django.contrib import admin

from ..models import (
    Checkbox, MultipleChoice, Page, RadioButton, SingleLineText,
)
from .page_admin import PageAdmin
from .question_admin import (
    FormQuestionChildAdmin, MultipleChoiceChildAdmin,
    MultipleChoiceParentAdmin,
)

admin.site.register(Page, PageAdmin)

admin.site.register(SingleLineText, FormQuestionChildAdmin)

admin.site.register(MultipleChoice, MultipleChoiceParentAdmin)
admin.site.register(Checkbox, MultipleChoiceChildAdmin)
admin.site.register(RadioButton, MultipleChoiceChildAdmin)
