from django.db import models
from django.contrib.auth import get_user_model


class Task(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	STATUS_CHOICES = [
		("todo", "To Do"),
		("in_progress", "In Progress"),
		("done", "Done"),
	]
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
	assigned_to = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

	def __str__(self) -> str:
		return self.title


class Location(models.Model):
	name = models.CharField(max_length=200)
	latitude = models.DecimalField(max_digits=9, decimal_places=6)
	longitude = models.DecimalField(max_digits=9, decimal_places=6)
	radius_meters = models.PositiveIntegerField(default=100)

	def __str__(self) -> str:
		return self.name


class Frequency(models.Model):
	METHODS = [
		("manual", "Manual"),
		("qr", "QR Code"),
		("geofence", "Geofencing"),
	]

	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	method = models.CharField(max_length=20, choices=METHODS)
	location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
	latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	confirmed = models.BooleanField(default=False)
	present = models.BooleanField(default=True)
	task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)
	suap_synced = models.BooleanField(default=False)

	class Meta:
		ordering = ["-timestamp"]

	def __str__(self) -> str:
		return f"{self.user} - {self.timestamp} - {self.method}"


class Justification(models.Model):
	frequency = models.OneToOneField(Frequency, on_delete=models.CASCADE)
	reason = models.TextField()
	attached_file = models.FileField(upload_to="justificativas/", null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"Justificativa {self.frequency_id}"


class SuapToken(models.Model):
	access_token = models.CharField(max_length=1024)
	refresh_token = models.CharField(max_length=1024, null=True, blank=True)
	token_type = models.CharField(max_length=64, null=True, blank=True)
	scope = models.CharField(max_length=256, null=True, blank=True)
	expires_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def is_valid(self):
		from django.utils import timezone
		if not self.expires_at:
			return True
		return self.expires_at > timezone.now()

	def __str__(self) -> str:
		return f"SUAP token (created {self.created_at.isoformat()})"


class AuditLog(models.Model):
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=16)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    auth_type = models.CharField(max_length=32)
    remote_addr = models.CharField(max_length=45, blank=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        user_label = self.user.username if self.user else 'anonymous'
        return f"AuditLog {self.method} {self.path} by {user_label}"
