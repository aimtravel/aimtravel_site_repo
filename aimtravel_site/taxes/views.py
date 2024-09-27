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
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import smart_str

from django.views import generic as views
from docxtpl import DocxTemplate
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from reportlab.pdfgen import canvas

from aimtravel_site import settings
from aimtravel_site.taxes.forms import *
from aimtravel_site.taxes.models import *
from aimtravel_site.posting.models import News

UserModel = get_user_model()


VALID_FILE_FIELDS = [
    'passport_copy',
    'visa_copy',
    'ssn_copy',
    'last_paycheck_doc',
    'w2_form',
    'w2_lpc_e3',
    'w2_lpc_e4',
    'bank_account_screenshot',
    'us_document_copy',
    'signed_and_scanned_contract'
]


def private_storage_permissions(request, field_name, private_file):
    if field_name not in VALID_FILE_FIELDS:
        raise Http404('Invalid field')

    try:
        tax = Taxes.objects.get(**{field_name: private_file})

        file_field = getattr(tax, field_name, None)

        if file_field and (request.user == tax.user or request.user.is_superuser):
            file_path = file_field.path
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        else:
            raise Http404("You are not allowed to view this file.")
    except Taxes.DoesNotExist:
        raise Http404("File not found")
    except ValueError:
        raise Http404("Invalid field")


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

    # success_url = reverse_lazy('edit tax')  # Replace 'success' with the actual URL name

    def get_form_kwargs(self):
        # Pass the logged-in user to the form
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

    def form_valid(self, form):
        # Set the user's info on the form instance before saving
        form.instance.user = self.request.user
        form.instance.first_name = self.request.user.first_name
        # last_name called in userAuth a.k.a. family_name in taxes model
        form.instance.family_name = self.request.user.last_name
        form.instance.email = self.request.user.email

        # Call the superclass's form_valid to continue the usual process
        # Save the form to get the created Taxes instance
        self.object = form.save()

        # Redirect to the edit tax page, passing the pk of the created Taxes instance
        return redirect(reverse('edit tax', kwargs={'pk': self.object.pk}))


class EditTaxesView(LoginRequiredMixin, views.UpdateView):
    model = Taxes
    form_class = EditTaxesForm
    template_name = 'taxes/edit_taxes.html'
    context_object_name = 'edit_taxes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['latest_tax'] = get_object_or_404(Taxes, user=self.request.user)
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
        if form.cleaned_data['last_paycheck_doc_clear']:
            if form.cleaned_data['last_paycheck_doc']:
                form.cleaned_data['last_paycheck_doc'].delete()
        if form.cleaned_data['w2_form_clear']:
            if form.cleaned_data['w2_form']:
                form.cleaned_data['w2_form'].delete()
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


class TaxEntryListView(LoginRequiredMixin, views.ListView):
    model = Taxes
    template_name = 'taxes/tax_entry_list.html'
    context_object_name = 'tax_list'
    ordering = ['id']

    def get_queryset(self):
        user_pk = self.kwargs['pk']
        return Taxes.objects.filter(user_id=user_pk).order_by('id')


def pre_add_tax(request):
    if UserModel:
        return render(request, 'taxes/pre-add-taxes.html')
    else:
        return render(request, 'user_auth/auth_page.html')

# def add_image_to_pdf(pdf_buffer, image_path, x, y, width, height):
#     """
#     Add an image to an existing PDF.
#     """
#     img = ImageReader(image_path)
#     pdf = canvas.Canvas(pdf_buffer)
#     pdf.drawImage(img, x, y, width=width, height=height)
#     pdf.save()
#
#
# def generate_pdf(request, tax_id):
#     # Fetch data from the database using the tax_id
#     contract_data = get_object_or_404(Taxes, id=tax_id)
#     today_date = timezone.now().date()
#     formatted_date = today_date.strftime("%d.%m.%Y")
#
#     template_relative_path = os.path.join(settings.BASE_DIR, 'templates', 'taxes', 'contract_template.docx')
#
#     # Render a .docx template with variables using python-docx-template
#     docx_template = DocxTemplate(template_relative_path)
#     context = {'contract_data': contract_data, 'today_date': formatted_date}
#     docx_template.render(context)
#
#     # Save the rendered .docx template to a BytesIO object
#     docx_stream = io.BytesIO()
#     docx_template.save(docx_stream)
#     docx_stream.seek(0)
#
#     # Load the .docx template
#     doc = Document(docx_stream)
#
#     jost_regular_path = os.path.join(settings.STATIC_URL, 'fonts', 'Jost', 'static', 'Jost-Regular.ttf')
#     jost_bold_path = os.path.join(settings.STATIC_URL, 'fonts', 'Jost', 'static', 'Jost-Bold.ttf')
#
#     # Register a font that supports Cyrillic characters
#     pdfmetrics.registerFont(TTFont('Jost-Regular', jost_regular_path))
#     pdfmetrics.registerFont(TTFont('Jost-Bold', jost_bold_path))
#
#     # Create a PDF using ReportLab
#     buffer = io.BytesIO()
#
#     # Create a PDF document
#     pdf = canvas.Canvas(buffer, pagesize=letter)
#
#     # Set up a margin
#     margin = 50
#
#     # Set up page dimensions
#     page_width, page_height = letter
#     max_height = page_height - 2 * margin
#
#     # Set the font and size
#     pdf.setFont("Jost-Regular", 10)  # Use your preferred font
#
#     height = max_height
#     line_spacing = 15
#
#     # Iterate through paragraphs in the .docx template
#     for paragraph in doc.paragraphs:
#         # Check for the remaining height on the current page
#         if height - line_spacing < margin:
#             pdf.showPage()
#             height = max_height
#             # Set the font and size for the new page
#             pdf.setFont("Jost-Regular", 10)  # Use your preferred font
#
#         # Check for bold formatting
#         if '**' in paragraph.text:
#             parts = paragraph.text.split('**')
#             for i, part in enumerate(parts):
#                 if i % 2 == 0:
#                     pdf.drawString(margin, height, part)
#                 else:
#                     # Bold formatting
#                     pdf.setFont("Jost-Bold", 10)  # Use your preferred bold font
#                     pdf.drawString(margin, height, part)
#                     pdf.setFont("Jost-Regular", 10)
#                 # # Move to the next line with increased spacing
#                 height -= line_spacing
#         else:
#             pdf.drawString(margin, height, paragraph.text)
#             # Move to the next line with increased spacing
#             height -= line_spacing
#
#     image_path = os.path.join(settings.BASE_DIR, 'static', 'img', '1.png')
#
#     add_image_to_pdf(buffer, image_path, margin, margin, width=100, height=100)
#     pdf.save()
#
#     # Return the modified PDF as an attachment
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="contract_{tax_id}.pdf"'
#
#     return response
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

    # Create a PDF using ReportLab
    output_pdf = io.BytesIO()
    pdf = canvas.Canvas(output_pdf, pagesize=letter)

    # logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'Ready-stock', 'Logo', 'color-logo.png')
    # logo = ImageReader(logo_path)
    # pdf.drawImage(logo, 225, 710, width=150, height=60)

    # Set up font paths
    jost_regular_path = os.path.join(settings.STATIC_URL, 'fonts', 'Jost', 'static', 'Jost-Regular.ttf')
    jost_bold_path = os.path.join(settings.STATIC_URL, 'fonts', 'Jost', 'static', 'Jost-Bold.ttf')

    # Register fonts
    pdfmetrics.registerFont(TTFont('Jost-Regular', jost_regular_path))
    pdfmetrics.registerFont(TTFont('Jost-Bold', jost_bold_path))

    # Set up a margin
    margin = 50

    # Set up page dimensions
    page_width, page_height = letter
    max_height = page_height - 2 * margin

    # Set the font and size
    pdf.setFont("Jost-Regular", 11)  # Use your preferred font

    # Iterate through paragraphs in the .docx template
    height = max_height
    line_spacing = 14
    for paragraph in doc.paragraphs:
        # Check for the remaining height on the current page
        if height - line_spacing < margin:
            pdf.showPage()
            height = max_height
            pdf.setFont("Jost-Regular", 11)  # Use your preferred font

        # Check for bold formatting
        if '**' in paragraph.text:
            parts = paragraph.text.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    pdf.drawString(margin, height, part)
                else:
                    # Bold formatting
                    pdf.setFont("Jost-Bold", 12)  # Use your preferred bold font
                    pdf.drawString(margin, height, part)
                    pdf.setFont("Jost-Regular", 11)
                height -= line_spacing
        else:
            pdf.drawString(margin, height, paragraph.text)
            height -= line_spacing
        # Check for bold formatting #2
        # for run in paragraph.runs:
        #     if run.bold:
        #         pdf.setFont("Jost-Bold", 12)  # Use bold font
        #     else:
        #         pdf.setFont("Jost-Regular", 11)
        #     pdf.drawString(margin, height, run.text)
        #     height -= line_spacing

    # Add image to the PDF
    image_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'sign.jpg')
    img = ImageReader(image_path)
    pdf.drawImage(img, 50, 260, width=100, height=50)

    # Save the PDF to output buffer
    pdf.save()

    # Return the modified PDF as an attachment
    output_pdf.seek(0)

    # Merge the generated PDF with another PDF
    # Load the generated PDF and another PDF (e.g., "appendix.pdf")
    generated_pdf = PdfReader(output_pdf)  # Generated PDF from ReportLab
    appendix_pdf_path = os.path.join(settings.BASE_DIR, 'templates', 'taxes', 'appendix.pdf')  # Path to the second PDF
    appendix_pdf = PdfReader(appendix_pdf_path)  # Load the appendix PDF

    # Create a new PdfWriter to combine PDFs
    pdf_writer = PdfWriter()

    # Add all pages from the generated PDF
    for page_num in range(len(generated_pdf.pages)):
        pdf_writer.add_page(generated_pdf.pages[page_num])

    # Add all pages from the appendix PDF
    for page_num in range(len(appendix_pdf.pages)):
        pdf_writer.add_page(appendix_pdf.pages[page_num])

    # Output combined PDF to a new buffer
    final_output_pdf = io.BytesIO()
    pdf_writer.write(final_output_pdf)
    final_output_pdf.seek(0)

    response = HttpResponse(final_output_pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{tax_id}.pdf"'

    return response


class AdminTaxEntryListView(UserPassesTestMixin, views.ListView):
    model = Taxes
    template_name = 'taxes/admin_tax_entry_list.html'
    context_object_name = 'tax_entries'
    ordering = ['-user', '-id']  # Order entries by primary key or another field

    def test_func(self):
        return self.request.user.is_staff


class SuperUserAddTaxesView(UserPassesTestMixin, views.CreateView):
    model = Taxes  # Replace YourModel with the actual model you're using
    form_class = AdminAddTaxes
    template_name = 'taxes/admin-add-tax.html'
    success_url = reverse_lazy('all-taxes')  # Replace 'success' with the actual URL name

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser


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
        if form.cleaned_data['last_paycheck_doc_clear']:
            if form.cleaned_data['last_paycheck_doc']:
                form.cleaned_data['last_paycheck_doc'].delete()
        if form.cleaned_data['w2_form_clear']:
            if form.cleaned_data['w2_form']:
                form.cleaned_data['w2_form'].delete()
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


def admin_send_application_view(request, taxes_pk):
    # Fetch the Taxes instance by the given taxes_pk
    taxes = get_object_or_404(Taxes, pk=taxes_pk)

    # Mark the taxes as sent
    taxes.is_sent = True
    taxes.save()

    # Retrieve the user associated with this taxes model
    user = taxes.user

    # Get the user's full name and email
    name = f"{user.first_name} {user.last_name}"  # Adjust based on Taxes model fields
    email = user.email
    recipient = email
    cc_email = ['vlzahariev@gmail.com']

    logo_path = "https://www.aimtravel.bg/static/img/Ready-stock/Logo/image001.png"

    subject = f"Връщане на Данъци от САЩ - регистрация"

    # Render HTML content for the email
    html_content = render_to_string('taxes/email_template.html', {'name': name, 'logo': logo_path})

    # Create a plain text version of the email content
    text_content = html.strip_tags(html_content)

    # Create and send the email
    email = EmailMultiAlternatives(subject, text_content, email, [recipient], cc=cc_email)
    email.attach_alternative(html_content, "text/html")
    email.send()
    success_url = reverse_lazy('admin_success_tax', kwargs={'taxes_pk': taxes.id})
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


def admin_success_page_view(request, taxes_pk):
    taxes = Taxes.objects.get(pk=taxes_pk)
    print(taxes.pk)
    return render(request, 'admin_success-taxes.html', {'taxes': taxes})
