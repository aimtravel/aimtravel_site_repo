import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from django.views import generic as views
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from aimtravel_site.taxes.forms import AddTaxes, TaxesDetailForm, EditTaxes
from aimtravel_site.taxes.models import Taxes
from aimtravel_site.posting.models import News


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
    success_url = reverse_lazy('success')  # Replace 'success' with the actual URL name

    def form_valid(self, form):
        # Additional logic if needed before saving the form
        return super().form_valid(form)


class EditTaxesView(LoginRequiredMixin, views.UpdateView):
    model = Taxes
    form_class = EditTaxes
    template_name = 'taxes/edit_taxes.html'
    context_object_name = 'edit_taxes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the latest Tax object associated with the user
        latest_tax = get_object_or_404(Taxes, user=self.request.user)

        # Add the latest_tax to the context
        context['latest_tax'] = latest_tax

        return context

    def get_success_url(self):
        taxes_pk = self.kwargs['pk']
        return reverse_lazy('detail tax', kwargs={'pk': taxes_pk})


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
    # Fetch data from the database using the contract_id
    contract_data = Taxes.objects.get(id=tax_id)
    first_name = contract_data.first_name
    last_name = contract_data.family_name

    # Render a Django template to generate the text file
    text_content = render(request, 'taxes/contract_template.txt',
                          {'contract_data': contract_data}).content.decode('utf-8')

    # Generate a PDF using ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{tax_id}.pdf"'

    # Calculate the absolute path to the font file
    font_path_regular = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../static/fonts/Jost/static/Jost-Regular.ttf'))
    font_path_bold = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../static/fonts/Jost/static/Jost-Bold.ttf'))

    # Register a font that supports Cyrillic characters
    pdfmetrics.registerFont(TTFont('Jost-Regular', font_path_regular))
    pdfmetrics.registerFont(TTFont('Jost-Bold', font_path_bold))
    # Create a PDF document
    pdf = canvas.Canvas(response, pagesize=letter)
    # Set up a margin
    margin = 30

    # Split the text content into lines
    lines = text_content.split('\n')

    # Calculate the starting height for the text
    height = letter[1] - margin

    # Set the font and size
    pdf.setFont("Jost-Regular", 12)  # Use the registered font

    line_spacing = 20

    # Draw each line on the PDF
    for line in lines:
        # Check for bold markers and adjust formatting
        if '**' in line:
            parts = line.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    pdf.drawString(margin, height, part)
                else:
                    # Bold formatting
                    pdf.setFont("Jost-Bold", 12)
                    pdf.drawString(margin, height, part)
                    pdf.setFont("Jost-Regular", 12)

                # Move to the next line with increased spacing
                height -= line_spacing
        else:
            pdf.drawString(margin, height, line)
            # Move to the next line with increased spacing
            height -= line_spacing

    pdf.save()

    return response
