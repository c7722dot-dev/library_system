from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Value
from django.db.models.functions import Replace

from catalog.models import BookCopy
from .models import Reader, Loan
from .serializers import ReaderSerializer, LoanSerializer, IssueLoanSerializer, ReturnLoanSerializer


# ─── Մասնաճյուղի օգնական ֆունկցիաներ ───────────────────────────────────────────

def get_active_branch(request):
    """
    Վերադարձնում է (branch_id, branch_info_dict, db_alias):
    branch_info-ն պարունակում է 'name'-ը Branch մոդելից (DB) և 'db'-ն settings-ից:
    """
    from catalog.models import Branch as BranchModel
    branch_dbs = settings.BRANCH_DATABASES

    # Վերցնում ենք ակտիվ մասնաճյուղը սեսիայից, կամ առաջինը ցանկից
    branch_id = request.session.get('active_branch_id', next(iter(branch_dbs)))
    if branch_id not in branch_dbs:
        branch_id = next(iter(branch_dbs))

    db_alias = branch_dbs[branch_id]['db']

    # Անունը վերցնում ենք տվյալների բազայից
    try:
        branch_obj = BranchModel.objects.get(pk=branch_id)
        name = branch_obj.name
    except BranchModel.DoesNotExist:
        name = db_alias  # fallback, եթե գրառումը բազայում չկա

    info = {'name': name, 'db': db_alias}
    return branch_id, info, db_alias


def get_all_branches_info():
    """
    Վերադարձնում է dict {branch_id: {'name': ..., 'db': ...}}
    բոլոր մասնաճյուղերի համար settings-ից, անունները վերցված են տվյալների բազայից:
    Օգտագործվում է նավբարում (մասնաճյուղի անջատիչ):
    """
    from catalog.models import Branch as BranchModel
    branch_dbs = settings.BRANCH_DATABASES
    result = {}
    for bid, cfg in branch_dbs.items():
        try:
            obj = BranchModel.objects.get(pk=bid)
            name = obj.name
        except BranchModel.DoesNotExist:
            name = cfg['db']
        result[bid] = {'name': name, 'db': cfg['db']}
    return result


def switch_branch(request):
    """Մասնաճյուղի փոխում GET ?branch_id=1 պարամետրով"""
    branch_id = int(request.GET.get('branch_id', 1))
    if branch_id in settings.BRANCH_DATABASES:
        request.session['active_branch_id'] = branch_id
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ─── Web տեսքեր (Views) ────────────────────────────────────────────────
def normalize_phone(phone):
    """Оставляем только цифры"""
    return ''.join(c for c in phone if c.isdigit())


def reader_list(request):
    branch_id, branch_info, db = get_active_branch(request)
    query = request.GET.get('q', '').strip()
    readers = Reader.objects.using(db).all()

    if query:
        # Оставляем только цифры из запроса
        digits_only = ''.join(c for c in query if c.isdigit())

        # Нормализуем телефон в БД — убираем все нецифровые символы
        readers_ann = readers.annotate(
            phone_digits=Replace(
                Replace(
                    Replace(
                        Replace(
                            Replace('phone', Value('+'), Value('')),
                            Value('-'), Value('')
                        ),
                        Value(' '), Value('')
                    ),
                    Value('('), Value('')
                ),
                Value(')'), Value('')
            )
        )

        q_filter = (
            Q(last_name__icontains=query)   |
            Q(first_name__icontains=query)  |
            Q(middle_name__icontains=query) |
            Q(card_number__icontains=query) |
            Q(phone__icontains=query)
        )

        # Если в запросе есть цифры — ищем по нормализованному телефону
        if digits_only:
            # 091111035 → убираем ведущий 0 → 91111035
            # 37491111035 → последние 8 цифр → 91111035
            # ищем вхождение в нормализованном телефоне
            short = digits_only.lstrip('0')  # убираем ведущие нули
            if short.startswith('374'):
                short = short[3:]  # убираем код страны 374

            q_filter |= Q(phone_digits__icontains=digits_only)
            if short:
                q_filter |= Q(phone_digits__icontains=short)

        readers = readers_ann.filter(q_filter)

    context = {
        'readers':          readers,
        'branch_info':      branch_info,
        'branches':         get_all_branches_info(),
        'active_branch_id': branch_id,
        'query':            query,
    }
    return render(request, 'lending/reader_list.html', context)


def loan_list(request):
    branch_id, branch_info, db = get_active_branch(request)
    status_filter = request.GET.get('status', 'active')

    loans = Loan.objects.using(db).select_related('reader')

    if status_filter == 'active':
        loans = loans.filter(returned_at__isnull=True)
    elif status_filter == 'returned':
        loans = loans.filter(returned_at__isnull=False)
    elif status_filter == 'overdue':
        loans = loans.filter(returned_at__isnull=True, due_date__lt=timezone.now().date())

    context = {
        'loans': loans,
        'branch_info': branch_info,
        'branches': get_all_branches_info(),
        'active_branch_id': branch_id,
        'status_filter': status_filter,
        'today': timezone.now().date(),
    }
    return render(request, 'lending/loan_list.html', context)


def issue_book(request):
    """Գրքի տրամադրում"""
    branch_id, branch_info, db = get_active_branch(request)

    if request.method == 'POST':
        copy_id = request.POST.get('book_copy_id')
        reader_id = request.POST.get('reader_id')
        due_days = int(request.POST.get('due_days', 14))

        try:
            copy = BookCopy.objects.get(pk=copy_id, status='available')
            reader = Reader.objects.using(db).get(pk=reader_id, is_active=True)

            loan = Loan(
                book_copy_id=copy.id,
                book_title=copy.book.title,
                inventory_number=copy.inventory_number,
                reader=reader,
                issued_at=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=due_days),
            )
            loan.save(using=db)

            # Թարմացնում ենք էկզեմպլյարի կարգավիճակը կենտրոնական տվյալների բազայում
            copy.status = 'lent'
            copy.save(using='default')

            messages.success(request, f'«{copy.book.title}» գիրքը տրամադրվել է {reader.full_name} ընթերցողին')
            return redirect('loan_list')

        except BookCopy.DoesNotExist:
            messages.error(request, 'Գրքի էկզեմպլյարը չի գտնվել կամ հասանելի չէ')
        except Reader.DoesNotExist:
            messages.error(request, 'Ընթերցողը չի գտնվել')

    available_copies = BookCopy.objects.filter(status='available').select_related('book', 'branch')
    readers = Reader.objects.using(db).filter(is_active=True)

    context = {
        'available_copies': available_copies,
        'readers': readers,
        'branch_info': branch_info,
        'branches': get_all_branches_info(),
        'active_branch_id': branch_id,
    }
    return render(request, 'lending/issue_book.html', context)


def return_book(request, loan_id):
    """Գրքի վերադարձ"""
    branch_id, branch_info, db = get_active_branch(request)
    loan = get_object_or_404(Loan.objects.using(db), pk=loan_id, returned_at__isnull=True)

    if request.method == 'POST':
        loan.returned_at = timezone.now().date()
        loan.save(using=db)

        # Վերադարձնում ենք էկզեմպլյարի կարգավիճակը
        BookCopy.objects.filter(pk=loan.book_copy_id).update(status='available')

        messages.success(request, f'«{loan.book_title}» գիրքը վերադարձվել է')
        return redirect('loan_list')

    return render(request, 'lending/return_book.html', {'loan': loan, 'branch_info': branch_info})


# ─── API ViewSets ─────────────────────────────────────────────

class ReaderViewSet(viewsets.ModelViewSet):
    serializer_class = ReaderSerializer

    def _get_db(self):
        branch_id = int(self.request.query_params.get('branch_id', 1))
        info = settings.BRANCH_DATABASES.get(branch_id, {})
        return info.get('db', 'branch_1')

    def get_queryset(self):
        return Reader.objects.using(self._get_db()).all()

    def perform_create(self, serializer):
        serializer.save(using=self._get_db())

    def save(self, using=None, *args, **kwargs):
        super().save(*args, **kwargs)


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer

    def _get_db(self):
        branch_id = int(self.request.query_params.get('branch_id', 1))
        info = settings.BRANCH_DATABASES.get(branch_id, {})
        return info.get('db', 'branch_1')

    def get_queryset(self):
        return Loan.objects.using(self._get_db()).select_related('reader')

    @action(detail=False, methods=['post'])
    def issue(self, request):
        """POST /api/loans/issue/ — տրամադրել գիրք"""
        ser = IssueLoanSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        db = self._get_db()

        try:
            copy = BookCopy.objects.get(pk=ser.validated_data['book_copy_id'], status='available')
            reader = Reader.objects.using(db).get(pk=ser.validated_data['reader_id'], is_active=True)
        except BookCopy.DoesNotExist:
            return Response({'error': 'Էկզեմպլյարը հասանելի չէ'}, status=status.HTTP_400_BAD_REQUEST)
        except Reader.DoesNotExist:
            return Response({'error': 'Ընթերցողը չի գտնվել'}, status=status.HTTP_400_BAD_REQUEST)

        due_days = ser.validated_data.get('due_days', 14)
        loan = Loan(
            book_copy_id=copy.id,
            book_title=copy.book.title,
            inventory_number=copy.inventory_number,
            reader=reader,
            issued_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=due_days),
            notes=ser.validated_data.get('notes', ''),
        )
        loan.save(using=db)
        copy.status = 'lent'
        copy.save(using='default')

        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """POST /api/loans/{id}/return_book/ — վերադարձնել գիրքը"""
        db = self._get_db()
        try:
            loan = Loan.objects.using(db).get(pk=pk, returned_at__isnull=True)
        except Loan.DoesNotExist:
            return Response({'error': 'Տրամադրումը չի գտնվել'}, status=status.HTTP_404_NOT_FOUND)

        loan.returned_at = timezone.now().date()
        loan.notes += f"\n{request.data.get('notes', '')}".rstrip()
        loan.save(using=db)
        BookCopy.objects.filter(pk=loan.book_copy_id).update(status='available')

        return Response(LoanSerializer(loan).data)


def add_reader(request):
    """Նոր ընթերցողի գրանցում աշխատակցի էջից"""
    branch_id, branch_info, db = get_active_branch(request)
    error = None

    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        phone       = request.POST.get('phone', '').strip()
        email       = request.POST.get('email', '').strip()
        card_number = request.POST.get('card_number', '').strip()

        if not first_name or not last_name or not card_number:
            error = 'Անունը, ազգանունը և տոմսի համարը պետք է լրացնել'
        elif Reader.objects.using(db).filter(card_number=card_number).exists():
            error = f'«{card_number}» տոմսի համարով ընթերցողն արդեն կա'
        else:
            Reader.objects.using(db).create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                phone=phone,
                email=email,
                card_number=card_number,
                is_active=True,
            )
            messages.success(request, f'Ընթերցող «{last_name} {first_name}» ({card_number}) գրանցված է')
            return redirect('reader_list')

    # Տոմսի հաջորդ համարի ավտոգեներացիա
    prefix = f'B{branch_id}-'
    existing = Reader.objects.using(db).filter(
        card_number__startswith=prefix
    ).order_by('card_number').values_list('card_number', flat=True)
    max_num = 0
    for cn in existing:
        try:
            max_num = max(max_num, int(cn.replace(prefix, '')))
        except ValueError:
            pass
    next_card = f'{prefix}{(max_num + 1):05d}'

    return render(request, 'lending/add_reader.html', {
        'branch_info': branch_info,
        'branches': get_all_branches_info(),
        'active_branch_id': branch_id,
        'next_card': next_card,
        'error': error,
        'form_data': request.POST if error else {},
    })