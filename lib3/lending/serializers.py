from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Reader, Loan


class ReaderSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    active_loans_count = serializers.SerializerMethodField()

    class Meta:
        model = Reader
        fields = ['id', 'first_name', 'last_name', 'middle_name',
                  'card_number', 'phone', 'email', 'registered_at',
                  'is_active', 'full_name', 'active_loans_count']

    def get_active_loans_count(self, obj):
        return obj.loans.filter(returned_at__isnull=True).count()


class LoanSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)
    is_returned = serializers.BooleanField(read_only=True)
    reader_name = serializers.CharField(source='reader.full_name', read_only=True)
    reader_card = serializers.CharField(source='reader.card_number', read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id', 'book_copy_id', 'book_title', 'inventory_number',
            'reader', 'reader_name', 'reader_card',
            'issued_at', 'due_date', 'returned_at', 'notes',
            'is_overdue', 'is_returned',
        ]


class IssueLoanSerializer(serializers.Serializer):
    """Сериализатор для выдачи книги"""
    book_copy_id = serializers.IntegerField()
    reader_id = serializers.IntegerField()
    due_days = serializers.IntegerField(default=14, min_value=1, max_value=90)
    notes = serializers.CharField(required=False, allow_blank=True)


class ReturnLoanSerializer(serializers.Serializer):
    """Сериализатор для возврата книги"""
    loan_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
