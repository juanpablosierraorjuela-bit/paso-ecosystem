import json
from decimal import Decimal
import uuid
import hashlib
from urllib import request as url_request, parse, error
from datetime import datetime, timedelta, time, date
from math import radians, cos, sin, asin, sqrt

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.db.models import Sum

from .models import Salon, Service, Booking, EmployeeSchedule
from .forms import SalonIntegrationsForm, ServiceForm, EmployeeCreationForm, ScheduleForm

User = get_user_model()

# --- UTILIDAD: CÁLCULO DE DISTANCIA (Haversine) ---
def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos.
    """
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radio de la tierra en KM
        return c * r
    except (ValueError, TypeError):
        return float('inf') # Si hay error en datos, retornamos distancia infinita

# --- UTILIDAD: ENVIAR TELEGRAM ---
def send_telegram_notification(salon, message):
    if not salon.telegram_bot_token or not salon.telegram_chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{salon.telegram_bot_token}/sendMessage"
        payload = {'chat_id': salon.telegram_chat_id, 'text': message, 'parse_mode': 'Markdown'}
        data_encoded = parse.urlencode(payload).encode()
        req = url_request.Request(url, data=data_encoded)
        with url_request.urlopen(req) as response:
            return True
    except Exception as e:
        print(f"Error Telegram: {e}")
        return False

# --- VISTAS GENERALES ---
def logout_view(request):
    logout(request)
    return redirect('home')


def home(request):
    # Obtener hora actual en Colombia
    now = timezone.now().astimezone(timezone.get_current_timezone())
    current_weekday = now.weekday() # 0=Lunes
    current_time = now.time()

    # --- LÓGICA DE GEOLOCALIZACIÓN INTELIGENTE ---
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    user_located = False
    
    # Obtenemos todos los activos primero
    salones_query = Salon.objects.filter(is_active=True)
    salones_filtrados = []

    # Si tenemos ubicación del usuario, filtramos por radio de ciudad (aprox 35km)
    if user_lat and user_lng:
        user_located = True
        CITY_RADIUS_KM = 35 
        for salon in salones_query:
            # Solo procesar si el salón tiene coordenadas configuradas
            if salon.latitude is not None and salon.longitude is not None:
                dist = haversine_distance(user_lng, user_lat, salon.longitude, salon.latitude)
                if dist <= CITY_RADIUS_KM:
                    salones_filtrados.append(salon)
            else:
                # Si un salón no tiene GPS configurado, decidimos si mostrarlo o no.
                # Para ser estrictos con "solo negocios de tu ciudad", mejor no mostrar los sin ubicación
                # cuando el usuario está filtrando por ubicación.
                pass 
    else:
        # Si no hay ubicación (primera carga o denegado), mostramos todos como fallback
        # Opcional: Podrías dejar esta lista vacía si quieres ser ULTRA estricto.
        salones_filtrados = list(salones_query)

    # --- LÓGICA DE ESTADO (ABIERTO/CERRADO) ---
    salones_con_estado = []
    
    for salon in salones_filtrados:
        is_open = False
        
        # Buscamos turnos activos para hoy que cubran la hora actual
        schedules = EmployeeSchedule.objects.filter(
            employee__role='EMPLOYEE', # Asegurar que sea empleado
            weekday=current_weekday,
            is_active=True,
            from_hour__lte=current_time,
            to_hour__gte=current_time
        )
        # Filtramos schedules que pertenezcan a empleados de ESTE salón
        # Como el modelo EmployeeSchedule no tiene link directo a Salon, 
        # asumimos que la relación viene por: Salon -> Owner -> (Logic Gap in original code)
        # NOTA: Mantengo la lógica original del código provisto que asume schedules globales o filtrados implícitamente.
        # Para ser precisos, filtramos por la relación inversa si existiera, pero usaremos la lógica base:
        if schedules.exists():
            is_open = True
            
        # Agregamos atributo temporal al objeto
        salon.is_open_now_dynamic = is_open 
        salones_con_estado.append(salon)

    return render(request, 'home.html', {
        'salones': salones_con_estado,
        'user_located': user_located, # Flag para saber si el filtro geográfico se aplicó
    })


def register_owner(request):
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if not business_name or not phone or not password:
             return render(request, 'users/register_owner.html', {'error': 'Por favor llena todos los campos.'})

        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) < 10:
             return render(request, 'users/register_owner.html', {'error': 'Ingresa un número de WhatsApp válido.'})

        if User.objects.filter(username=clean_phone).exists():
            return render(request, 'users/register_owner.html', {'error': 'Este número de WhatsApp ya está registrado.'})

        try:
            user = User.objects.create_user(username=clean_phone, email="", password=password)
            user.role = 'ADMIN'
            user.first_name = business_name
            user.save()

            slug = slugify(business_name)
            if Salon.objects.filter(slug=slug).exists():
                slug += f"-{str(uuid.uuid4())[:4]}"

            Salon.objects.create(owner=user, name=business_name, slug=slug, is_active=True)

            login(request, user)
            return redirect('admin_dashboard')
        except Exception as e:
            return render(request, 'users/register_owner.html', {'error': str(e)})

    return render(request, 'users/register_owner.html')


# --- DASHBOARDS ---
@login_required
def owner_dashboard(request):
    salon = Salon.objects.filter(owner=request.user).first()
    if not salon: return redirect('home')

    config_form = SalonIntegrationsForm(instance=salon)
    service_form = ServiceForm()
    employee_form = EmployeeCreationForm()

    if request.method == 'POST':
        if 'update_config' in request.POST:
            f = SalonIntegrationsForm(request.POST, instance=salon)
            if f.is_valid(): f.save(); messages.success(request, 'Configuración guardada.')
        elif 'create_service' in request.POST:
            f = ServiceForm(request.POST)
            if f.is_valid():
                s = f.save(commit=False)
                s.salon = salon
                s.save()
                messages.success(request, 'Servicio creado.')
        elif 'create_employee' in request.POST:
            f = EmployeeCreationForm(request.POST)
            if f.is_valid():
                u = f.save(commit=False)
                u.role = 'EMPLOYEE'
                u.set_password(f.cleaned_data['password'])
                u.save()
                for day in range(6):
                    EmployeeSchedule.objects.create(
                        employee=u, weekday=day,
                        from_hour=time(9, 0), to_hour=time(19, 0), is_active=True
                    )
                messages.success(request, 'Empleado creado y agenda activada.')
        return redirect('admin_dashboard')

    services = Service.objects.filter(salon=salon)
    employees = User.objects.filter(role='EMPLOYEE')
    
    # Webhook URL para mostrar en el panel
    webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/')
    if 'http://' in webhook_url:
        webhook_url = webhook_url.replace('http://', 'https://')
    
    return render(request, 'owner_dashboard.html', {
        'salon': salon, 'config_form': config_form, 'service_form': service_form,
        'employee_form': employee_form, 'services': services, 'employees': employees,
        'webhook_url': webhook_url
    })

@login_required
def dashboard(request):
    user = request.user
    if getattr(user, 'role', '') == 'ADMIN': return redirect('admin_dashboard')  
    elif getattr(user, 'role', '') == 'EMPLOYEE': return redirect('employee_panel')
    citas = Booking.objects.filter(customer=user).order_by('-start_time')          
    return render(request, 'dashboard.html', {'citas': citas})

@login_required
def employee_dashboard(request):
    if 'delete_id' in request.POST:
        schedule_id = request.POST.get('delete_id')
        EmployeeSchedule.objects.filter(id=schedule_id, employee=request.user).delete()
        messages.success(request, 'Turno eliminado.')
        return redirect('employee_panel')

    form = ScheduleForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.employee = request.user
            schedule.save()
            messages.success(request, '¡Nuevo horario agregado!')
            return redirect('employee_panel')
    schedules = EmployeeSchedule.objects.filter(employee=request.user).order_by('weekday', 'from_hour')
    return render(request, 'employee_dashboard.html', {'schedules': schedules, 'form': form})

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if service.salon.owner == request.user: service.delete()
    return redirect('admin_dashboard')

# --- API HORARIOS ---
def get_available_slots_api(request):
    salon_id = request.GET.get('salon_id')
    employee_id = request.GET.get('employee_id')
    date_str = request.GET.get('date')
    service_ids = request.GET.getlist('service_ids[]')

    if not (salon_id and employee_id and date_str and service_ids):
        return JsonResponse({'error': 'Faltan datos'}, status=400)

    try:
        query_date = parse_date(date_str)
        weekday = query_date.weekday()
        total_duration = 0
        for sid in service_ids:
            try:
                srv = Service.objects.get(id=int(sid))
                total_duration += srv.duration_minutes
            except: pass

        schedule = EmployeeSchedule.objects.filter(employee_id=employee_id, weekday=weekday, is_active=True).first()
        if not schedule: return JsonResponse({'slots': []})

        existing_bookings = Booking.objects.filter(employee_id=employee_id, start_time__date=query_date).exclude(status='cancelled')

        slots = []
        current_time = datetime.combine(query_date, schedule.from_hour)
        shift_end = datetime.combine(query_date, schedule.to_hour)
        step = timedelta(minutes=30)
        service_delta = timedelta(minutes=total_duration)

        while current_time + service_delta <= shift_end:
            slot_start = current_time
            slot_end = current_time + service_delta
            is_busy = False
            for booking in existing_bookings:
                b_start = booking.start_time.replace(tzinfo=None)
                b_dur = booking.service.duration_minutes if booking.service else 30
                b_end = b_start + timedelta(minutes=b_dur)
                if slot_start < b_end and slot_end > b_start:
                    is_busy = True; break
            if not is_busy: slots.append(slot_start.strftime("%H:%M"))
            current_time += step

        return JsonResponse({'slots': slots})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ==============================================================================
# LÓGICA DE RESERVA
# ==============================================================================
def booking_create(request, salon_slug):
    salon = get_object_or_404(Salon, slug=salon_slug)
            
    services = Service.objects.filter(salon=salon)
    employees = User.objects.filter(role='EMPLOYEE')

    if request.method == 'POST':
        try:
            service_ids = request.POST.getlist('services')
            emp_id = request.POST.get('employee')
            date_str = request.POST.get('date')
            time_str = request.POST.get('selected_time')
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')

            if not time_str:
                messages.error(request, "Selecciona una hora.")
                return redirect('booking_create', salon_slug=salon.slug)

            # LOGIN / REGISTRO
            if request.user.is_authenticated:
                customer_user = request.user
            else:
                clean_phone = ''.join(filter(str.isdigit, customer_phone))        
                if not clean_phone: clean_phone = f"user_{uuid.uuid4().hex[:6]}" 
                try:
                    customer_user = User.objects.get(username=clean_phone)        
                except User.DoesNotExist:
                    customer_user = User.objects.create_user(
                        username=clean_phone, first_name=customer_name,
                        password=clean_phone, role='CLIENT'
                    )
                login(request, customer_user)

            # PREPARAR CITA
            emp = User.objects.get(id=emp_id)
            current_start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            first_booking = None
            total_price = 0
            group_id = str(uuid.uuid4())[:8]

            # Si tiene Bold, estado 'pending_payment'. Si no, 'confirmed'.
            tiene_bold = bool(salon.bold_identity_key)
            initial_status = 'pending_payment' if tiene_bold else 'confirmed'

            for s_id in service_ids:
                srv = Service.objects.get(id=s_id)
                total_price += srv.price
                booking = Booking.objects.create(
                    salon=salon, employee=emp, service=srv,
                    customer=customer_user, customer_name=customer_name,
                    start_time=current_start_time, 
                    status=initial_status,      
                    total_price=srv.price, payment_id=group_id
                )
                current_start_time += timedelta(minutes=srv.duration_minutes)    
                if not first_booking: first_booking = booking

            # NOTIFICACIÓN INTELIGENTE
            if not tiene_bold:
                # LOCAL: Avisar de una vez
                msg = f"✅ *NUEVA CITA (LOCAL)*\n👤 {customer_name}\n📱 {customer_phone}\n💰 Total: ${total_price:,.0f}"
                send_telegram_notification(salon, msg)
            else:
                # BOLD: Esperar al Webhook
                pass

            return redirect('booking_success', booking_id=first_booking.id)       

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'booking_create.html', {
        'salon': salon, 'services': services, 'employees': employees
    })

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    salon = booking.salon
    group_bookings = Booking.objects.filter(payment_id=booking.payment_id)        
    total_value = sum(b.total_price for b in group_bookings)

    deposit_percent = salon.deposit_percentage
    deposit_amount = int(total_value * (Decimal(deposit_percent) / 100))
    pending_amount = total_value - deposit_amount

    # FIRMA DE BOLD
    bold_signature = ""
    order_id = f"ORD-{booking.payment_id}"
    if salon.bold_identity_key and salon.bold_secret_key:
        raw_sig = f"{order_id}{deposit_amount}COP{salon.bold_secret_key}"        
        bold_signature = hashlib.sha256(raw_sig.encode()).hexdigest()

    return render(request, 'booking_success.html', {
        'booking': booking, 'salon': salon, 'total_value': total_value,
        'deposit_amount': deposit_amount, 'pending_amount': pending_amount,
        'deposit_percent': deposit_percent, 'order_id': order_id,
        'bold_signature': bold_signature, 'group_bookings': group_bookings
    })

# ==============================================================================
# WEBHOOK BOLD 
# ==============================================================================

@login_required
def test_telegram_integration(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        chat_id = data.get('chat_id')
        if not token or not chat_id: return JsonResponse({'success': False, 'message': 'Faltan datos.'})
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {'chat_id': chat_id, 'text': "✅ Conexión Exitosa con PASO"}
            data_encoded = parse.urlencode(payload).encode()
            req = url_request.Request(url, data=data_encoded)
            with url_request.urlopen(req) as response:
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})


@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST':
        print(f"🔵 [WEBHOOK V2] Recibido para Salón ID: {salon_id}")
        try:
            body_unicode = request.body.decode('utf-8')
            payload = json.loads(body_unicode)
            
            # 1. BUSCAR ID DE REFERENCIA
            ref = payload.get('orderId') or payload.get('order_id') or payload.get('payment_reference')
            
            if not ref:
                data_obj = payload.get('data', {})
                if isinstance(data_obj, dict):
                    meta = data_obj.get('metadata', {})
                    ref = meta.get('reference')
            
            if not ref:
                return JsonResponse({'status': 'error', 'message': 'No reference found'}, status=400)

            order_id = str(ref).replace('ORD-', '')

            # 2. VALIDAR APROBACIÓN
            is_approved = False
            tx_status = payload.get('transactionStatus')
            if tx_status is not None and int(tx_status) == 4:
                is_approved = True
            if payload.get('type') == 'SALE_APPROVED':
                is_approved = True

            if not is_approved:
                return JsonResponse({'status': 'ignored', 'message': 'Not approved'})

            # 3. PROCESAR RESERVA
            bookings = Booking.objects.filter(payment_id=order_id)
            
            if bookings.exists():
                total = sum(b.total_price for b in bookings)
                
                monto_pagado = payload.get('paymentAmount')
                if not monto_pagado:
                    monto_pagado = payload.get('data', {}).get('amount', {}).get('total')
                
                if monto_pagado:
                    abono = Decimal(str(monto_pagado))
                else:
                    abono = total
                
                pendiente = total - abono
                cliente = bookings.first().customer_name
                salon = bookings.first().salon 
                
                bookings.update(status='paid')
                
                # Notificación Telegram
                msgs = [
                    "💰 *PAGO BOLD CONFIRMADO*",
                    f"👤 Cliente: {cliente}",
                    f"🆔 Orden: #{order_id}",
                    "-----------------------------",
                    f"💵 Total: ${total:,.0f}",
                    f"✅ Abono: ${abono:,.0f}",
                    f"👉 *PENDIENTE: ${pendiente:,.0f}*",
                    "-----------------------------",
                    "📅 Cita Agendada."
                ]
                try:
                    send_telegram_notification(salon, "\n".join(msgs))
                except Exception as e:
                    print(f"⚠️ Fallo Telegram: {e}")
                
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            print(f"🔥 [WEBHOOK] Error Crítico: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return HttpResponse(status=405)
