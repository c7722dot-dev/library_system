from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from catalog import views as cat_views
from lending import views as lend_views

router = DefaultRouter()
router.register(r'books',    cat_views.BookViewSet,    basename='book')
router.register(r'branches', cat_views.BranchViewSet,  basename='branch')
router.register(r'authors',  cat_views.AuthorViewSet,  basename='author')
router.register(r'readers',  lend_views.ReaderViewSet, basename='reader')
router.register(r'loans',    lend_views.LoanViewSet,   basename='loan')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Web
    path('',             cat_views.book_list,     name='book_list'),
    path('books/<int:pk>/', cat_views.book_detail, name='book_detail'),
    path('books/<int:book_pk>/add-copy/', cat_views.add_copy, name='add_copy'),
    path('books/import/',          cat_views.bulk_add_books, name='bulk_add_books'),
    path('books/import/template/', cat_views.csv_template,   name='csv_template'),
    path('branches/manage/',  cat_views.branch_manage, name='branch_manage'),
    path('branches/add/',     cat_views.branch_add,    name='branch_add'),
    path('readers/',        lend_views.reader_list, name='reader_list'),
    path('readers/add/',    lend_views.add_reader,  name='add_reader'),
    path('loans/',       lend_views.loan_list,    name='loan_list'),
    path('loans/issue/', lend_views.issue_book,   name='issue_book'),
    path('loans/<int:loan_id>/return/', lend_views.return_book, name='return_book'),
    path('switch-branch/', lend_views.switch_branch, name='switch_branch'),
    # REST API
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)