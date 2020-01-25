from django.contrib import admin
from first_app.models import Topic, Webpage, AccessRecord, UserProfileInfo

# super_user: qiuchenzhang
# email: qiuchenzhang94@gmail.com
# password: zqc94828


# Register your models here.
admin.site.register(Topic)
admin.site.register(Webpage)
admin.site.register(AccessRecord)

# Login and register
admin.site.register(UserProfileInfo)