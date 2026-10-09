from django.urls import path

from .views import (
	AcceptPickupView,
	AdminPickupListView,
	AvailableVolunteerPickupsView,
	ConfirmReceivedView,
	DeliveryProofView,
	DonorPickupListView,
	NGOPickupListView,
	PickupDetailView,
	PickupStatusView,
	ScheduleNGOPickupView,
	VolunteerAssignmentsView,
)

urlpatterns = [
	path('volunteer/assignments/', VolunteerAssignmentsView.as_view(), name='volunteer-assignments'),
	path('volunteer/available/', AvailableVolunteerPickupsView.as_view(), name='volunteer-available-pickups'),
	path('volunteer/pickups/<int:pickup_id>/accept/', AcceptPickupView.as_view(), name='volunteer-accept-pickup'),
	path('pickups/my-donor/', DonorPickupListView.as_view(), name='donor-pickups'),
	path('admin/pickups/', AdminPickupListView.as_view(), name='admin-pickups'),
	path('pickups/<int:pickup_id>/', PickupDetailView.as_view(), name='pickup-detail'),
	path('pickups/<int:pickup_id>/proof/', DeliveryProofView.as_view(), name='pickup-proof'),
	path('pickups/<int:pickup_id>/status/', PickupStatusView.as_view(), name='pickup-status'),
	path('ngo/pickups/', NGOPickupListView.as_view(), name='ngo-pickups'),
	path('donations/<int:donation_id>/schedule-pickup/', ScheduleNGOPickupView.as_view(), name='schedule-ngo-pickup'),
	path('pickups/<int:pickup_id>/confirm-received/', ConfirmReceivedView.as_view(), name='confirm-ngo-received'),
]
