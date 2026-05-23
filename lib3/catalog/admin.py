from django.contrib import admin
from django.utils.html import format_html
from .models import Branch, Author, Genre, Book, BookCopy


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'db_alias', 'is_active', 'switch_button']
    list_filter = ['is_active']
    search_fields = ['name', 'address']

    def switch_button(self, obj):
        return format_html(
            '<a class="button" href="/switch-branch/?branch_id={}" '
            'style="background:#417690;color:white;padding:4px 10px;'
            'border-radius:4px;text-decoration:none;font-size:12px;">'
            '🔀 Անցնել</a>',
            obj.pk
        )
    switch_button.short_description = 'Փոխել մասնաճյուղը'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'birth_year']
    search_fields = ['last_name', 'first_name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 0
    fields = ['branch', 'inventory_number', 'status']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_authors', 'genre', 'year', 'isbn']
    list_filter = ['genre', 'year']
    search_fields = ['title', 'isbn', 'authors__last_name']
    filter_horizontal = ['authors']
    inlines = [BookCopyInline]

    def get_authors(self, obj):
        return ', '.join(str(a) for a in obj.authors.all())
    get_authors.short_description = 'Հեղինակներ'


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ['book', 'branch', 'inventory_number', 'status']
    list_filter = ['branch', 'status']
    search_fields = ['book__title', 'inventory_number']