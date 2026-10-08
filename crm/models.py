from django.conf import settings
from django.db import models


class Tag(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_tags")
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="unique_crm_tag_owner_name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    STATUS_CHOICES = [("lead", "Lead"), ("prospect", "Prospect"), ("customer", "Customer"), ("inactive", "Inactive"), ("lost", "Lost")]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_contacts")
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="lead")
    source = models.CharField(max_length=50, default="manual")
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="contacts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["owner", "phone"], name="unique_crm_owner_phone")]

    def __str__(self):
        return self.company_name or self.name


class ContactNote(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="activity_notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Segment(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_segments")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    rules = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Subscription(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_subscription")
    product = models.CharField(max_length=50, default="crm")
    status = models.CharField(max_length=30, choices=[("active", "Active"), ("trial", "Trial"), ("expired", "Expired")], default="trial")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)


class CRMConfiguration(models.Model):
    INDUSTRIES = [("school", "School"), ("shop", "Small Shop"), ("business", "Small Business")]
    MODULES = [("contacts", "Contacts"), ("tags", "Tags"), ("segments", "Segments"), ("attendance", "Attendance"), ("transactions", "Sales & Purchases"), ("notes", "Notes & Activity"), ("import_export", "Import & Export")]
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_configuration")
    industry = models.CharField(max_length=30, choices=INDUSTRIES, default="business")
    modules = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)


class Attendance(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late")])
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StaffMember(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_members")
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    pay_type = models.CharField(max_length=20, choices=[("monthly", "Monthly salary"), ("hourly", "Hourly / part-time")], default="monthly")
    pay_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    standard_hours = models.DecimalField(max_digits=6, decimal_places=2, default=8)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StaffAttendance(models.Model):
    member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late")])
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["member", "date"], name="unique_staff_attendance_date")]


class InventoryTransaction(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crm_transactions")
    kind = models.CharField(max_length=20, choices=[("sale", "Sale"), ("purchase", "Purchase")])
    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.quantity * self.unit_price
