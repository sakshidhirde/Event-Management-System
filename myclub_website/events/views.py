from django.shortcuts import render, redirect

import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event, Venue
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter 
from django.core.paginator import Paginator




# Generate PDF file in Venue List 

def venue_pdf(request):
    
    # create Bytestream buffer
    buf = io.BytesIO()
    
    # create a canvas 
    c= canvas.Canvas(buf, pagesize=letter, bottomup=0)
    
    # creat a text object 
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    
    # Designate the model 
    venues = Venue.objects.all()
    
    # create blank list
    lines=[]
    
    # for loop 
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append("=====================")
        
    # for loop in lines 
    for line in lines:
        textob.textLine(line)
    # Finish up
    c.drawText(textob)
    c.shoPage()
    c.save()
    buf.seek(0)
    
    return FileResponse(buf, as_attachment=True, filename='venue.pdf')


# Generate CSV file in Venue List
def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['content-Disposition'] = 'attachment; filename=venue.csv'
    
    # Create a csv writer
    writer = csv.writer(response)
    
    # Designate the Model
    venues = Venue.objects.all()
    
    # Add column heading to the csv file
    writer.writerow(['Venue Name', 'Addresss', 'Zip Code', 'Phone', 'Web Address', 'Email'])
    
    # for loop
    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code, venue.phone, venue.web, venue.email_address])
        
    return response

    
 


# Generate text file in Venue List
def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['content-Disposition'] = 'attachment; filename=venue.txt'
    
    # Designate the Model
    venues = Venue.objects.all()
    
    #create blank list
    lines=[]
    
    #for loop 
    for venue in venues:
        lines.append(f'{venue.name}\n {venue.address}\n {venue.zip_code}\n {venue.phone}\n {venue.web}\n {venue.email_address}\n \n \n')
        
    #  write to textfile
    response.writelines(lines)
    return response


# Delete Event
def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('list-events')

# Delete Venue
def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')

# Add Event
def add_event(request):
    submitted = False
    if request.method=="POST":
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user    # Logged In User
                event.save()
                #form.save()
                return HttpResponseRedirect('/add_event?submitted=True')      
        
    else:
        # Just Going To The Page, Not Submitting 
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm
        if 'submitted' in request.GET :
            submitted=True
    return render(request, 'events/add_event.html', {'form':form, 'submitted': submitted})

# Update Event
def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)
        
    if form.is_valid():
        form.save()
        return redirect('list-events')

    return render(request,
                  'events/update_event.html', {
                      "event":event,
                      "form": form
                  })
    

# Update Venue
def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')

    return render(request,
                  'events/update_venue.html', {
                      "venue":venue,
                      "form": form
                  })
    

# Search Venue
def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name = searched)
        return render(request, 'events/search_venues.html',
                      {"searched": searched,
                       "venues": venues})        
    else:
        return render(request, 'search_venues.html', {})
        

# Show Venue
def show_venue(request, venue_id):
    venue =Venue.objects.get(pk=venue_id)

    return render(request,
                  'events/show_venue.html', {
                      "venue":venue
                  })


# List Venue
def list_venues(request):
    #venue_list=Venue.objects.all().order_by('name')  #order wise or arranging order - any elements there like phone_no etc.
    
    venue_list=Venue.objects.all()
    
    # set up pagination
    p = Paginator(Venue.objects.all(), 3)
    page = request.GET.get('page')
    
    venues = p.get_page(page)
    
    nums = "a" * venues.paginator.num_pages
    
    

    return render(request,
                  'events/venue.html', {
                      "venue_list":venue_list,
                      "venues": venues, 
                      "nums":nums
                  })

# Add Venue
def add_venue(request):
    submitted = False
    if request.method=="POST":
        form=VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id      # logged in User
            venue.save()
            #form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form=VenueForm()
        if 'submitted' in request.GET :
            submitted=True
    return render(request, 'events/add_venue.html', {'form':form, 'submitted': submitted})

# All Event
def all_event(request):
    event_list=Event.objects.all().order_by('name')

    return render(request,
                  'events/event_list.html', {
                      "event_list":event_list
                  })

# home
def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name="Sakshi"
    month = month.capitalize()

    month_number = list(calendar.month_name).index(month)
    month_number=int(month_number)
    cal=HTMLCalendar().formatmonth(year, month_number)
    now=datetime.now()
    current_year = now.year
    time=now.strftime('%I:%M:%S %p')

    return render(request, 
        'events/home.html', {
        "name":name,
        "year":year,
        "month":month,
        "month_number":month_number,
        "cal":cal,
        "current_year":current_year,
        "time":time})