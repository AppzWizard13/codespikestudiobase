import json
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse
from orders.models import Payment, Order, TempOrder  # import your actual models
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import requests
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import json
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import requests
from .models import PaymentAPILog  # Ensure this is correct
from django.utils.timezone import now

import json
import requests
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from .models import PaymentAPILog
from django.db.models import Q



def initiate_cashfree_payment(request, order):
    """
    Sends a payment link creation request to Cashfree and redirects to the link or a failure page.
    """

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'payment_method': 'cashfree',
            'amount': order.total,
            'status': Payment.Status.PENDING
        }
    )

    if not created:
        payment.payment_method = 'cashfree'
        payment.amount = order.total
        payment.status = Payment.Status.PENDING
        payment.save()

    return_url = request.build_absolute_uri(reverse('cashfree_return')) + f"?order_id={order.order_number}"
    webhook_url = request.build_absolute_uri(reverse('cashfree_webhook'))

    payload = {
        "customer_details": {
            "customer_email": order.customer.email,
            "customer_name": order.customer.username,
            "customer_phone": order.customer.phone_number
        },
        "link_amount": float(order.total),
        "link_currency": "INR",
        "link_id": order.order_number,
        "link_meta": {
            "notify_url": webhook_url,
            "return_url": return_url,
            "upi_intent": False
        },
        "link_notify": {
            "send_email": True,
            "send_sms": True
        },
        "link_purpose": f"Payment for Order #{order.order_number}"
    }

    headers = {
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://sandbox.cashfree.com/pg/links", json=payload, headers=headers)
        res_data = response.json()

        PaymentAPILog.objects.create(
            order=order,
            action='CREATE_LINK',
            request_url="https://sandbox.cashfree.com/pg/links",
            request_payload=json.dumps(payload),
            response_status=response.status_code,
            response_body=json.dumps(res_data),
            link_id=res_data.get("link_id")
        )
    except Exception as e:
        PaymentAPILog.objects.create(
            order=order,
            action='ERROR',
            request_url="https://sandbox.cashfree.com/pg/links",
            request_payload=json.dumps(payload),
            error_message=str(e)
        )
        return redirect('payment_failed')

    if response.status_code == 200 and res_data.get("link_url"):
        payment.transaction_id = res_data.get("link_id")
        payment.gateway_response = res_data
        payment.save()

        return redirect(res_data["link_url"])
    
    if res_data.get("message") == "Link ID already exists":
        order_id = order.order_number  # e.g., "ORD-20250511-0021"
        
        # Check if a log exists with this link_id inside response_body
        payment_log = PaymentAPILog.objects.filter(
            Q(response_body__contains=f'"link_id": "{order_id}"'),
            response_status=200
        ).first()

        print("payment_log:", payment_log)
        
        if payment_log:
            response_data = json.loads(payment_log.response_body)
            link_id = response_data.get("link_id")
            return redirect(response_data["link_url"])

    return redirect('payment_failed')




@csrf_exempt
def cashfree_webhook(request):
    # Create log entry at the start
    log_entry = PaymentAPILog.objects.create(
        action='WEBHOOK',
        request_url=request.path,
        response_body=request.body.decode('utf-8') if request.body else None,
        response_status=0,  # Will update later
    )
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("datadatadatadatadata", data)
            order_id = data.get('data', {}).get('link_id')  # e.g., CF_ORD123
            print("order_idorder_idorder_id", order_id)
            payment_status = data.get('order', {}).get('order_status')  # e.g., PAID, FAILED

            # if not order_id:
            #     error_msg = 'Missing order_id'
            #     log_entry.error_message = error_msg
            #     log_entry.status_code = 400
            #     log_entry.save()
            #     return JsonResponse({'error': error_msg}, status=400)

            # payment = Payment.objects.filter(transaction_id=order_id).first()
            # if not payment:
            #     error_msg = 'Payment not found'
            #     log_entry.error_message = error_msg
            #     log_entry.status_code = 404
            #     log_entry.save()
            #     return JsonResponse({'error': error_msg}, status=404)

            # # Update payment status
            # if payment_status == 'PAID':
            #     payment.status = Payment.Status.COMPLETED
            #     payment.order.payment_status = Order.PaymentStatus.COMPLETED
            #     payment.order.status = Order.Status.PROCESSING
            # elif payment_status in ['FAILED', 'EXPIRED']:
            #     payment.status = Payment.Status.FAILED
            #     payment.order.payment_status = Order.PaymentStatus.FAILED

            # payment.gateway_response = data
            # payment.save()
            # payment.order.save()

            # Update log entry for successful processing
            log_entry.status_code = 200
            log_entry.response_data = {'status': 'success', 'order_id': order_id, 'payment_status': payment_status}
            log_entry.save()

            return HttpResponse(status=200)

        except Exception as e:
            print("eeeeeeeeeeeeeeeeee", e)
            error_msg = str(e)
            log_entry.error_message = error_msg
            return HttpResponse(status=200)



def cashfree_return(request):
    order_id = request.GET.get('order_id')  # e.g., CF_ORD123
    print("order_idorder_idorder_idorder_id", order_id)
    if not order_id:
        return render(request, 'advadmin/payment_failed.html', {'message': 'Missing order ID'})

    payment = Payment.objects.filter(transaction_id=order_id).first()
    if not payment:
        print("11111111111")
        return render(request, 'advadmin/payment_failed.html', {'message': 'Payment not found'})

    # Check and update status if needed (you can verify via Cashfree status API if needed)
    if payment.status == Payment.Status.COMPLETED:
        print("11111111111")
        request.session[f'order_{payment.order.order_number}_completed'] = True
        TempOrder.objects.filter(user=payment.order.user, processed=False).update(processed=True)
        return redirect('cashfree_order_success', pk=payment.order.id)
    else:
        print("11111111111")
        return render(request, 'advadmin/payment_failed.html', {'message': 'Payment was not successful'})




# In your payments/views.py or appropriate views.py file
def payment_failed(request):
    print("111111111111155")
    return render(request, 'advadmin/payment_failed.html', {'message': 'Payment Failed'})



