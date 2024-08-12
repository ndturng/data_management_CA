import pandas as pd
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PersonForm
from .models import Person


def people_list(request):
    people = Person.objects.all()
    return render(request, "people/people_list.html", {"people": people})


def person_create(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()

        if "file" in request.FILES:
            file = request.FILES["file"]
            data = pd.read_excel(file)

            for _, row in data.iterrows():
                Person.objects.create(
                    name=row["name"],
                    date_of_birth=row["date_of_birth"],
                    address=row["address"],
                )
            return redirect("person_list")
    else:
        form = PersonForm()
    return render(request, "people/person_form.html", {"form": form})


def person_update(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.method == "POST":
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect("person_list")
    else:
        form = PersonForm(instance=person)
    return render(request, "people/person_form.html", {"form": form})


def person_delete(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.method == "POST":
        person.delete()
        return redirect("people_list")
    return render(
        request, "people/person_confirm_delete.html", {"person": person}
    )
