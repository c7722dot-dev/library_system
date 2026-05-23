from django.db import models
from django.utils import timezone


class Reader(models.Model):
    """Ընթերցող (պահվում է մասնաճյուղի տվյալների բազայում)"""
    first_name = models.CharField('Անուն', max_length=100)
    last_name = models.CharField('Ազգանուն', max_length=100)
    middle_name = models.CharField('Հայրանուն', max_length=100, blank=True)
    card_number = models.CharField('Ընթերցողի տոմսի համար', max_length=30, unique=True)
    phone = models.CharField('Հեռախոս', max_length=30, blank=True)
    email = models.EmailField('Էլ. փոստ', blank=True)
    registered_at = models.DateField('Գրանցման ամսաթիվ', default=timezone.now)
    is_active = models.BooleanField('Ակտիվ է', default=True)

    class Meta:
        app_label = 'lending'
        verbose_name = 'Ընթերցող'
        verbose_name_plural = 'Ընթերցողներ'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.card_number})'

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p)


class Loan(models.Model):
    """Գրքի տրամադրում (պահվում է մասնաճյուղի տվյալների բազայում)"""
    # Հղում ենք կենտրոնական տվյալների բազայից օրինակի ID-ին (ոչ FK, քանի որ տարբեր ՏԲ են)
    book_copy_id = models.PositiveIntegerField('Գրքի օրինակի ID')
    book_title = models.CharField('Գրքի անվանում', max_length=300)   # ապանորմալիզացիա արագության համար
    inventory_number = models.CharField('Գույքագրման համար', max_length=50)

    reader = models.ForeignKey(
        Reader, on_delete=models.PROTECT,
        verbose_name='Ընթերցող', related_name='loans'
    )
    issued_at = models.DateField('Տրամադրման ամսաթիվ', default=timezone.now)
    due_date = models.DateField('Վերադարձի վերջնաժամկետ')
    returned_at = models.DateField('Վերադարձի ամսաթիվ', null=True, blank=True)
    notes = models.TextField('Նշումներ', blank=True)

    class Meta:
        app_label = 'lending'
        verbose_name = 'Գրքի տրամադրում'
        verbose_name_plural = 'Գրքերի տրամադրումներ'
        ordering = ['-issued_at']

    def __str__(self):
        status = 'վերադարձված' if self.returned_at else 'ընթերցողի մոտ'
        return f'{self.book_title} → {self.reader} [{status}]'

    @property
    def is_overdue(self):
        if self.returned_at:
            return False
        return timezone.now().date() > self.due_date

    @property
    def is_returned(self):
        return self.returned_at is not None