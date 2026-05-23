from django.db import models


class Branch(models.Model):
    """Գրադարանի մասնաճյուղ"""
    name     = models.CharField('Անվանում', max_length=200)
    address  = models.CharField('Հասցե', max_length=300)
    phone    = models.CharField('Հեռախոս', max_length=30, blank=True)
    db_alias = models.CharField(
        'Տվյալների բազայի այլանուն', max_length=50,
        help_text='Օրինակ՝ branch_1, branch_2'
    )
    is_active = models.BooleanField('Ակտիվ է', default=True)

    class Meta:
        verbose_name        = 'Մասնաճյուղ'
        verbose_name_plural = 'Մասնաճյուղեր'

    def __str__(self):
        return self.name


class Author(models.Model):
    """Գրքի հեղինակ"""
    first_name = models.CharField('Անուն', max_length=100)
    last_name  = models.CharField('Ազգանուն', max_length=100)
    birth_year = models.PositiveSmallIntegerField('Ծննդյան տարի', null=True, blank=True)

    class Meta:
        verbose_name        = 'Հեղինակ'
        verbose_name_plural = 'Հեղինակներ'
        ordering            = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Genre(models.Model):
    """Ժանր"""
    name = models.CharField('Ժանր', max_length=100, unique=True)

    class Meta:
        verbose_name        = 'Ժանր'
        verbose_name_plural = 'Ժանրեր'

    def __str__(self):
        return self.name


class Book(models.Model):
    """Գիրքը գլոբալ կատալոգում"""

    LANGUAGE_CHOICES = [
        ('hy',    'Հայերեն'),
        ('ru',    'Русский'),
        ('en',    'English'),
        ('fr',    'Français'),
        ('de',    'Deutsch'),
        ('ar',    'العربية'),
        ('other', 'Այլ'),
    ]

    title       = models.CharField('Անվանում', max_length=300)
    authors     = models.ManyToManyField(Author, verbose_name='Հեղինակներ', blank=True)
    genre       = models.ForeignKey(
        Genre, verbose_name='Ժանր',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    isbn        = models.CharField('ISBN', max_length=20, unique=True, blank=True)
    year        = models.PositiveSmallIntegerField('Հրատարակման տարի', null=True, blank=True)
    description = models.TextField('Նկարագրություն', blank=True)
    cover       = models.ImageField('Շապիկ', upload_to='covers/', null=True, blank=True)
    language    = models.CharField(
        'Լեզու', max_length=10,
        choices=LANGUAGE_CHOICES,
        default='hy', blank=True
    )

    class Meta:
        verbose_name        = 'Գիրք'
        verbose_name_plural = 'Գրքեր'
        ordering            = ['title']

    def __str__(self):
        return self.title


class BookCopy(models.Model):
    """Գրքի օրինակ կոնկրետ մասնաճյուղում"""

    STATUS_CHOICES = [
        ('available', 'Հասանելի է'),
        ('lent',      'Տրամադրված է'),
        ('lost',      'Կորցված'),
        ('damaged',   'Վնասված'),
    ]

    book             = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        verbose_name='Գիրք', related_name='copies'
    )
    branch           = models.ForeignKey(
        Branch, on_delete=models.CASCADE,
        verbose_name='Մասնաճյուղ', related_name='copies'
    )
    inventory_number = models.CharField('Գույքագրման համար', max_length=50, unique=True)
    status           = models.CharField(
        'Կարգավիճակ', max_length=20,
        choices=STATUS_CHOICES, default='available'
    )

    class Meta:
        verbose_name        = 'Գրքի օրինակ'
        verbose_name_plural = 'Գրքի օրինակներ'

    def __str__(self):
        return f'{self.book.title} [{self.inventory_number}] — {self.get_status_display()}'