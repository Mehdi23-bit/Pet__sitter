import django_filters
from django.db.models import Q
from .models import PetSitterProfile as Sitter
 
 
class SitterFilter(django_filters.FilterSet):
    # --- Location (text match, geocoded distance handled separately in the view) ---
    city = django_filters.CharFilter(field_name='user__city', lookup_expr='icontains')
 
    # --- Price range ---
    min_rate = django_filters.NumberFilter(field_name='price_per_day', lookup_expr='gte')
    max_rate = django_filters.NumberFilter(field_name='price_per_day', lookup_expr='lte')
 
    # --- Reviews / quality floor ---
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
 
    # --- Subscription toggle (let searchers optionally show premium-only) ---
    premium_only = django_filters.BooleanFilter(method='filter_premium_only')
 
    # --- Pet type handled (adjust field_name to match your actual model:
    #     if it's a ManyToMany to a PetType model, this works as-is;
    #     if it's a CharField/choices, swap lookup_expr accordingly) ---
    pet_type = django_filters.CharFilter(method='filter_pet_type')
 
    # --- Availability: needs BOTH start_date and end_date to actually filter ---
    start_date = django_filters.DateFilter(method='filter_availability')
    end_date = django_filters.DateFilter(method='filter_availability')
 
    # --- lat/lng are accepted here just so DRF doesn't reject them as unknown
    #     params; the real distance computation happens in the view ---
    lat = django_filters.NumberFilter(method='noop')
    lng = django_filters.NumberFilter(method='noop')
 
    class Meta:
        model = Sitter
        fields = []
 
    def noop(self, queryset, name, value):
        return queryset
 
    def filter_premium_only(self, queryset, name, value):
        if value:
            return queryset.filter(is_premium=True)
        return queryset
 
    def filter_pet_type(self, queryset, name, value):
        if value is None:
            return queryset
        value = value.lower().strip()

        mapping = {
          "dog"   : "accept_dogs",
          "dogs"  : "accept_dogs",
          "cat"   : "accept_cats",
          "cats"  : "accept_cats",
          "other" : "accept_other",
          "other" : "accept_other",
        }
        field_name = mapping[value]
        if field_name:
            return queryset.filter(**{field_name:True})
        return queryset.none()
 
    def filter_availability(self, queryset, name, value):
        start = self.data.get('start_date')
        end = self.data.get('end_date')
        if not (start and end):
            return queryset
 
        # ADJUST: assumes a related `bookings` model with start_date/end_date/status.
        overlapping = Q(
            contactrequest__start_date__lte=end,
            contactrequest__end_date__gte=start,
            contactrequest__status__in=['acepted', 'confirmed'],
        )
        return queryset.exclude(overlapping).distinct()
 

