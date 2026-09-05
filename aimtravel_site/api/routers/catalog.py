"""Read-only catalogue content: prices, services, employers, team and FAQ."""
from django.shortcuts import get_object_or_404
from ninja import Router

from aimtravel_site.api import schemas
from aimtravel_site.posting.models import Faq
from aimtravel_site.user_profile.models import Employee
from aimtravel_site.web.models import AdditionalServices, Company, Prices

router = Router()


@router.get('/prices', response=schemas.PricesOut | None, url_name='prices')
def current_prices(request):
    """The active price list.

    Only the most recent row is ever shown; older rows are kept as history.
    """
    return schemas.PricesOut.from_model(Prices.objects.order_by('-id').first())


@router.get('/services', response=list[schemas.AdditionalServiceOut])
def list_services(request):
    return list(AdditionalServices.objects.order_by('id'))


@router.get('/employers', response=list[schemas.CompanyOut])
def list_employers(request):
    return list(Company.objects.order_by('employer_name'))


@router.get('/employers/{int:company_id}', response=schemas.CompanyOut)
def employer_detail(request, company_id: int):
    return get_object_or_404(Company, pk=company_id)


@router.get('/team', response=list[schemas.EmployeeOut])
def list_team(request):
    team = Employee.objects.order_by('employee_first_name')
    return [schemas.EmployeeOut.from_model(e) for e in team]


@router.get('/faq', response=list[schemas.FaqOut])
def list_faq(request):
    return [schemas.FaqOut.from_model(f) for f in Faq.objects.order_by('id')]
