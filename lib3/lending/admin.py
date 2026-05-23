from django.contrib import admin
from django.conf import settings
from .models import Reader, Loan

def get_branch_db(request):
    """Կարդում ենք ընտրված մասնաճյուղը սեսիայից, լռելյայն՝ առաջինը:"""
    branch_dbs = list(settings.BRANCH_DATABASES.keys())
    branch_id = request.session.get('active_branch_id', branch_dbs[0])
    return settings.BRANCH_DATABASES.get(branch_id, {}).get('db', 'branch_1')


class BranchAdminMixin:
    """Միքսին. բոլոր queryset-ները գնում են ընթացիկ մասնաճյուղի տվյալների բազա:"""

    def get_queryset(self, request):
        db = get_branch_db(request)
        return super().get_queryset(request).using(db)

    def save_model(self, request, obj, form, change):
        db = get_branch_db(request)
        obj.save(using=db)

    def delete_model(self, request, obj):
        db = get_branch_db(request)
        obj.delete(using=db)


@admin.register(Reader)
class ReaderAdmin(BranchAdminMixin, admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'card_number', 'phone', 'registered_at', 'is_active']
    list_filter = ['is_active', 'registered_at']
    search_fields = ['last_name', 'first_name', 'card_number', 'phone']


@admin.register(Loan)
class LoanAdmin(BranchAdminMixin, admin.ModelAdmin):
    list_display = ['book_title', 'inventory_number', 'reader', 'issued_at', 'due_date', 'returned_at', 'overdue_flag']
    list_filter = ['returned_at', 'issued_at']
    search_fields = ['book_title', 'inventory_number', 'reader__last_name', 'reader__card_number']
    date_hierarchy = 'issued_at'

    def overdue_flag(self, obj):
        if obj.is_returned:
            return '✅ Վերադարձված'
        if obj.is_overdue:
            return '🔴 Ժամկետանց'
        return '🟡 Ընթերցողի մոտ'
    overdue_flag.short_description = 'Կարգավիճակ'