from django.contrib import admin, messages

from .models import Application, ApplicationStatus, ContractCounter, ContractDocument
from .services import ContractGenerationError
from .tasks import send_contract_email_task


class ContractDocumentInline(admin.StackedInline):
    model = ContractDocument
    readonly_fields = ("generated_at", "email_sent_at")
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("contract_number", "full_name_latin", "email", "office",
                    "season", "program_option", "status", "created_at")
    list_filter = ("status", "office", "season", "program_option")
    search_fields = ("contract_number", "email", "first_name", "last_name", "phone")
    date_hierarchy = "created_at"
    inlines = [ContractDocumentInline]
    actions = ["resend_email", "regenerate_contract"]

    # ЕГН и лична карта се четат, но не се редактират от админа — договорът
    # вече е издаден с тях и промяна тук би го направила невалиден.
    readonly_fields = ("public_id", "contract_number", "egn", "id_card_number",
                       "created_at", "consent_ip", "consent_user_agent",
                       "accepted_terms_at", "declared_truth_at", "accepted_gdpr_at")

    @admin.action(description="Изпрати имейла отново")
    def resend_email(self, request, queryset):
        sent, failed = 0, []
        for application in queryset.select_related("contract_document"):
            document = getattr(application, "contract_document", None)
            if document is None:
                continue
            document.email_sent_at = None
            document.save(update_fields=["email_sent_at"])
            # Задачата засега се изпълнява синхронно и връща дали имейлът е
            # тръгнал — затова тук можем да кажем истината на агента.
            if send_contract_email_task.delay(application.pk, document.pk):
                sent += 1
            else:
                failed.append(application.contract_number)
        if sent:
            self.message_user(request, f"Изпратени {sent} имейла.")
        if failed:
            self.message_user(
                request,
                f"Неуспешно изпращане за: {', '.join(failed)}. Виж лога на сървъра.",
                level=messages.ERROR,
            )

    @admin.action(description="Генерирай договора отново")
    def regenerate_contract(self, request, queryset):
        from django.core.files import File

        from .contracts import render_contract

        for application in queryset:
            try:
                rendered = render_contract(application)
            except (ContractGenerationError, Exception) as exc:
                self.message_user(request, f"{application.contract_number}: {exc}",
                                  level=messages.ERROR)
                continue
            document, _ = ContractDocument.objects.get_or_create(application=application)
            with open(rendered.pdf_path, "rb") as pdf:
                document.pdf.save(rendered.pdf_path.name, File(pdf), save=True)
            application.mark(ApplicationStatus.CONTRACT_ISSUED)
            self.message_user(request, f"{application.contract_number}: готов.")


@admin.register(ContractCounter)
class ContractCounterAdmin(admin.ModelAdmin):
    list_display = ("office", "season", "last_number")
    # Ръчна промяна на брояча може да произведе дублиран номер на договор.
    readonly_fields = ("office", "season", "last_number")

    def has_add_permission(self, request):
        return False
