import base64
import os
import io
from email.mime.image import MIMEImage
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.forms import formset_factory
from django.template.loader import render_to_string
from django.utils import timezone, html

import xlwt
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import smart_str

from django.views import generic as views
from docxtpl import DocxTemplate
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from reportlab.pdfgen import canvas

from aimtravel_site import settings
from aimtravel_site.taxes.forms import *
from aimtravel_site.taxes.models import *
from aimtravel_site.posting.models import News

UserModel = get_user_model()


class TaxMainView(views.ListView):
    template_name = 'nav/taxes.html'
    context_object_name = 'tax_view'

    def get_last_news(self):
        return News.objects.latest('date')

    def get(self, request, **kwargs):
        # Get the first 4 News items
        news_queryset = News.objects.order_by('-date')[:4]

        last_news_item = self.get_last_news()

        context = {
            'last_4_news': news_queryset,
            'very_last_news': last_news_item,
        }

        return render(request, self.template_name, context)


class AddTaxesView(LoginRequiredMixin, views.CreateView):
    model = Taxes  # Replace YourModel with the actual model you're using
    form_class = AddTaxes
    template_name = 'taxes/add-taxes-form.html'
    success_url = reverse_lazy('all-taxes')  # Replace 'success' with the actual URL name

    def form_valid(self, form):
        # Additional logic if needed before saving the form
        return super().form_valid(form)


class EditTaxesView(LoginRequiredMixin, views.UpdateView):
    model = Taxes
    form_class = EditTaxesForm
    template_name = 'taxes/edit_taxes.html'
    context_object_name = 'edit_taxes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_tax'] = get_object_or_404(Taxes, user=self.request.user)
        return context

    def get_success_url(self):
        taxes_pk = self.kwargs['pk']
        return reverse_lazy('edit tax', kwargs={'pk': taxes_pk})

    def form_valid(self, form):
        # Check and handle clearing and deleting for file_field1

        if form.cleaned_data['passport_copy_clear']:
            if form.cleaned_data['passport_copy']:
                form.cleaned_data['passport_copy'].delete()
        if form.cleaned_data['visa_copy_clear']:
            if form.cleaned_data['visa_copy']:
                form.cleaned_data['visa_copy'].delete()
        if form.cleaned_data['ssn_copy_clear']:
            if form.cleaned_data['ssn_copy']:
                form.cleaned_data['ssn_copy'].delete()
        if form.cleaned_data['last_paycheck_w2_clear']:
            if form.cleaned_data['last_paycheck_w2']:
                form.cleaned_data['last_paycheck_w2'].delete()
        if form.cleaned_data['bank_account_screenshot_clear']:
            if form.cleaned_data['bank_account_screenshot']:
                form.cleaned_data['bank_account_screenshot'].delete()
        if form.cleaned_data['us_document_copy_clear']:
            if form.cleaned_data['us_document_copy']:
                form.cleaned_data['us_document_copy'].delete()
        if form.cleaned_data['signed_and_scanned_contract_clear']:
            if form.cleaned_data['signed_and_scanned_contract']:
                form.cleaned_data['signed_and_scanned_contract'].delete()

        # Save the form data (or perform other necessary actions)
        return super().form_valid(form)


class DetailsTaxView(LoginRequiredMixin, views.DetailView):
    model = Taxes
    template_name = 'taxes/details_taxes.html'
    form_class = TaxesDetailForm
    context_object_name = 'details_taxes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the latest Tax object associated with the user
        latest_tax = get_object_or_404(Taxes, user=self.request.user)

        # Add the latest_tax to the context
        context['latest_tax'] = latest_tax

        return context


def pre_add_tax(request):
    latest_tax = None

    if request.user.is_authenticated:
        latest_tax = get_object_or_404(Taxes, user=request.user)

    return render(request, 'taxes/pre-add-taxes.html', {'latest_tax': latest_tax})


def generate_pdf(request, tax_id):
    # Fetch data from the database using the tax_id
    contract_data = get_object_or_404(Taxes, id=tax_id)
    today_date = timezone.now().date()
    formatted_date = today_date.strftime("%d.%m.%Y")

    template_relative_path = os.path.join(settings.BASE_DIR, 'templates', 'taxes', 'contract_template.docx')

    # Render a .docx template with variables using python-docx-template
    docx_template = DocxTemplate(template_relative_path)
    context = {'contract_data': contract_data, 'today_date': formatted_date}
    docx_template.render(context)

    # Save the rendered .docx template to a BytesIO object
    docx_stream = io.BytesIO()
    docx_template.save(docx_stream)
    docx_stream.seek(0)

    # Load the .docx template
    doc = Document(docx_stream)

    jost_regular_path = os.path.join(settings.STATIC_URL, 'fonts', 'Jost', 'static', 'Jost-Regular.ttf')
    jost_bold_path = os.path.join(settings.STATIC_URL, 'fonts', 'Jost', 'static', 'Jost-Bold.ttf')

    # Register a font that supports Cyrillic characters
    pdfmetrics.registerFont(TTFont('Jost-Regular', jost_regular_path))
    pdfmetrics.registerFont(TTFont('Jost-Bold', jost_bold_path))

    # Create a PDF using ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{tax_id}.pdf"'

    # Create a PDF document
    pdf = canvas.Canvas(response, pagesize=letter)

    # Set up a margin
    margin = 50

    # Set up page dimensions
    page_width, page_height = letter
    max_height = page_height - 2 * margin

    # Set the font and size
    pdf.setFont("Jost-Regular", 10)  # Use your preferred font

    height = max_height
    line_spacing = 15

    # Iterate through paragraphs in the .docx template
    for paragraph in doc.paragraphs:
        # Check for the remaining height on the current page
        if height - line_spacing < margin:
            pdf.showPage()
            height = max_height
            # Set the font and size for the new page
            pdf.setFont("Jost-Regular", 10)  # Use your preferred font

        # Check for bold formatting
        if '**' in paragraph.text:
            parts = paragraph.text.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    pdf.drawString(margin, height, part)
                else:
                    # Bold formatting
                    pdf.setFont("Jost-Bold", 10)  # Use your preferred bold font
                    pdf.drawString(margin, height, part)
                    pdf.setFont("Jost-Regular", 10)
                # # Move to the next line with increased spacing
                height -= line_spacing
        else:
            pdf.drawString(margin, height, paragraph.text)
            # Move to the next line with increased spacing
            height -= line_spacing

    pdf.save()

    return response


class AdminTaxEntryListView(UserPassesTestMixin, views.ListView):
    model = Taxes
    template_name = 'taxes/admin_tax_entry_list.html'
    context_object_name = 'tax_entries'
    ordering = ['user']  # Order entries by primary key or another field

    def test_func(self):
        return self.request.user.is_staff


class SuperuserEditTaxView(UserPassesTestMixin, views.UpdateView):
    model = Taxes
    form_class = AdminEditTaxes
    template_name = 'taxes/admin-edit-tax.html'  # Replace with your actual template
    success_url = reverse_lazy('all-taxes')  # Replace with your actual success URL

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        # Get the TaxEntry object based on the primary key from the URL
        return Taxes.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the currently clicked entry's pk to the context
        context['clicked_entry_pk'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        # Check and handle clearing and deleting for file_field1

        if form.cleaned_data['passport_copy_clear']:
            if form.cleaned_data['passport_copy']:
                form.cleaned_data['passport_copy'].delete()
        if form.cleaned_data['visa_copy_clear']:
            if form.cleaned_data['visa_copy']:
                form.cleaned_data['visa_copy'].delete()
        if form.cleaned_data['ssn_copy_clear']:
            if form.cleaned_data['ssn_copy']:
                form.cleaned_data['ssn_copy'].delete()
        if form.cleaned_data['last_paycheck_w2_clear']:
            if form.cleaned_data['last_paycheck_w2']:
                form.cleaned_data['last_paycheck_w2'].delete()
        if form.cleaned_data['bank_account_screenshot_clear']:
            if form.cleaned_data['bank_account_screenshot']:
                form.cleaned_data['bank_account_screenshot'].delete()
        if form.cleaned_data['us_document_copy_clear']:
            if form.cleaned_data['us_document_copy']:
                form.cleaned_data['us_document_copy'].delete()
        if form.cleaned_data['signed_and_scanned_contract_clear']:
            if form.cleaned_data['signed_and_scanned_contract']:
                form.cleaned_data['signed_and_scanned_contract'].delete()

        # Save the form data (or perform other necessary actions)
        return super().form_valid(form)


def send_application_view(request):
    taxes = Taxes.objects.filter(user_id=request.user.id)

    if taxes is not None:
        taxes = taxes.latest('id')
        taxes.is_sent = True
        taxes.save()

    name = f"{request.user.first_name} {request.user.last_name}"
    email = request.user.email
    recipient = email
    cc_email = ['vlzahariev@gmail.com']

    logo_path = "https://www.aimtravel.bg/static/img/Ready-stock/Logo/image001.png"

    subject = f"Връщане на Данъци от САЩ - регистрация"

    # Render HTML content for the email
    html_content = render_to_string('taxes/email_template.html', {'name': name, 'logo': logo_path})

    # Create a plain text version of the email content
    text_content = html.strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, email, [recipient], cc=cc_email)
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()
    success_url = reverse_lazy('success_tax', kwargs={'taxes_pk': taxes.id})
    return redirect(success_url)


class SuperuserDeleteTaxView(LoginRequiredMixin, UserPassesTestMixin, views.DeleteView):
    model = Taxes
    form_class = AdminEditTaxes
    template_name = 'taxes/admin-delete-tax.html'  # Replace with your actual template
    context_object_name = 'delete_tax'
    template_name_suffix = '_confirm_delete'
    success_url = reverse_lazy('all-taxes')  # Replace with your actual success URL

    def test_func(self):
        return self.request.user.is_staff


class ExportTaxesView(views.View):
    def get(self, request, *args, **kwargs):
        # Fetch the data you want to export
        taxes_data = Taxes.objects.all()

        # Choose the export format based on the URL parameter (?format=csv or ?format=xls)
        export_format = request.GET.get('format', 'xls')

        # Create the response object based on the selected format
        response = self.get_export_response(export_format)

        # Write data to response
        self.write_data_to_response(response, taxes_data, export_format)

        return response

    def get_export_response(self, export_format):
        response = HttpResponse(content_type=f'text/{export_format}')
        response['Content-Disposition'] = f'attachment; filename="taxes.{export_format}"'
        return response

    def write_data_to_response(self, response, data, export_format):
        # if export_format == 'csv':
        #     writer = csv.writer(response)
        #     self.write_csv_data(writer, data)
        if export_format == 'xls':
            self.write_xls_data(response, data)

    # def write_csv_data(self, writer, data):
    #     # Write CSV header
    #     writer.writerow(
    #         ['Име', 'Презиме', 'Фамилия', 'Mothers maiden name', 'Дата на раждане', 'Град на раждане', '	Адрес',
    #          'Град', 'Държава', 'Email', 'Телефон', 'Как научихте за нас', 'Social Security Number(SSN)',
    #          'Работна година', 'Дата на пристигане в САЩ', 'Дата на заминаване от САЩ', 'Тип виза', 'Тип програма',
    #          'Предишни декларации', 'Предишна промяна на виза', 'ПИН от IRS', 'Име на работодател',
    #          'Адрес на работодател', 'Град на работодател', 'Щат на работодател', 'ZIP код на работодател',
    #          'Телефон на работодател', 'Факс на работодател', 'Email на работодател', 'Последен чек', 'W2 форма',
    #          'Американска банкова сметка', 'Вид сметка', 'Име на банката', 'Собственик на сметката', 'Routing номер',
    #          'IBAN'])  # Add your model fields here

    # Write CSV data
    # for item in data:
    #     writer.writerow(
    #         [item.first_name, item.middle_name, item.family_name, item.mothers_maiden_name,
    #          item.birth_date, item.birth_city, item.address, item.city, item.country,
    #          item.email, item.phone_number, item.how_did_you_find_us, item.social_security,
    #          item.working_year, item.arrival_date_in_usa, item.departure_date_in_usa,
    #          item.visa_type, item.program_type, item.previous_tax_declarations,
    #          item.visa_changing, item.pin_from_irs, item.company_name, item.company_address,
    #          item.company_city, item.company_state, item.company_zip, item.company_phone,
    #          item.company_fax, item.company_email, item.last_paycheck, item.w_2,
    #          item.american_bank_account, item.type_of_account, item.bank_name,
    #          item.account_holder, item.routing_number, item.account_number
    #          ])  # Replace field1, field2, field3 with your actual field names

    def write_xls_data(self, response, data):
        # Create a new workbook and add a sheet
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Taxes')

        # Write Excel header
        header = ['Име',
                  'Фамилия',
                  'Social Security Number(SSN)',
                  'Email',
                  'Телефон',
                  'W2 форма',
                  'Очаквани документи',
                  'Статус',
                  'Стойност Federal',
                  'Стойност State',
                  'Комисионна Federal',
                  'Комисионна State'
                  ]  # Add your model fields here
        for col_num, value in enumerate(header):
            worksheet.write(0, col_num, value)

        # Write Excel data
        for row_num, item in enumerate(data, 1):
            worksheet.write(row_num, 0, item.first_name)
            worksheet.write(row_num, 1, item.family_name)
            worksheet.write(row_num, 2, item.social_security)
            worksheet.write(row_num, 3, item.email)
            worksheet.write(row_num, 4, item.phone_number)
            worksheet.write(row_num, 5, item.w_2)
            worksheet.write(row_num, 6, item.waiting_docs)
            worksheet.write(row_num, 7, item.general_status)
            worksheet.write(row_num, 8, item.federal_amount)
            worksheet.write(row_num, 9, item.state_amount)
            worksheet.write(row_num, 10, item.fee_federal)
            worksheet.write(row_num, 11, item.fee_state)
            # Replace field1, field2, field3 with your actual field names

        # Save the workbook to the response
        workbook.save(response)


def success_page_view(request, taxes_pk):
    taxes = Taxes.objects.get(pk=taxes_pk)
    print(taxes.pk)
    return render(request, 'success-taxes.html', {'taxes': taxes})
