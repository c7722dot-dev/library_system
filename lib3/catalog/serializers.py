from rest_framework import serializers
from .models import Branch, Author, Genre, Book, BookCopy


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone', 'is_active']


class BookCopySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BookCopy
        fields = ['id', 'inventory_number', 'branch', 'branch_name', 'status', 'status_display']


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    genre = GenreSerializer(read_only=True)
    copies = BookCopySerializer(many=True, read_only=True)
    available_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'genre', 'isbn', 'year', 'description', 'available_count', 'copies']

    def get_available_count(self, obj):
        return obj.copies.filter(status='available').count()


class BookListSerializer(serializers.ModelSerializer):
    """Облегчённый сериализатор для списка книг"""
    authors = serializers.StringRelatedField(many=True)
    genre = serializers.StringRelatedField()
    available_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'genre', 'isbn', 'year', 'available_count']

    def get_available_count(self, obj):
        return obj.copies.filter(status='available').count()
