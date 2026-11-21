import django.db
from django.db.models import Q, F
from core.models import Employee, Course

query_or = Employee.objects.filter(Q(department__code="IT") | Q(salary__gt=70000))
print("OR Query:", list(query_or))
print("SQL:", query_or.query)

query_not = Employee.objects.filter(Q(first_name__icontains="John") & ~Q(department__code="HR"))
print("AND NOT Query:", list(query_not))

django.db.reset_queries()
for emp in Employee.objects.all():
    print("Unopt:", emp.first_name, emp.department.name)
print("Total Queries (Unoptimized):", len(django.db.connection.queries))

django.db.reset_queries()
for emp in Employee.objects.select_related("department").all():
    print("select_related:", emp.first_name, emp.department.name)
print("Total Queries with select_related:", len(django.db.connection.queries))

django.db.reset_queries()
for course in Course.objects.prefetch_related("attendees").all():
    names = [emp.first_name for emp in course.attendees.all()]
    print("prefetch_related:", course.code, names)
print("Total Queries with prefetch_related:", len(django.db.connection.queries))