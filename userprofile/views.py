from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.http import Http404, HttpResponse, JsonResponse
from accounts.models import CustomUser
from .models import Address
from django.core.paginator import Paginator, EmptyPage
from accounts.models import CustomUser
from django.shortcuts import render, get_object_or_404
from cart.models import Order, OrderItem
from django.contrib.auth.hashers import make_password
import os
from io import BytesIO
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from store.models import *
from django.contrib.auth import update_session_auth_hash
# Create your views here.

def UserProfile(request):
    if 'useremail' in request.session:
        email = request.session['useremail']
        user = CustomUser.objects.get(email = email)
        user_id = user.id
        address = Address.objects.filter(user_id = user_id)
        context = {
            'users': user,
            'address': address
        }
    else:
        return redirect('user_login')
    return render(request,'userprofile/user_profile.html',context)



def EditUserProfile(request, user_id):
    if request.method ==  'POST':
        user = CustomUser.objects.get(id = user_id)

        if user :
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.phone = request.POST.get('phone')
            user.save()

            return redirect('user_profile')
        


def AddAddress(request, user_id):
    if request.method == 'POST':
            user = CustomUser.objects.get(pk = user_id)
            user_id = user
            house_no = request.POST.get('house_no')
            recipient_name = request.POST.get('RecipientName')
            street_name =  request.POST.get('street_name')
            village_name = request.POST.get('Village')
            postal_code = request.POST.get('postal_code')
            district = request.POST.get('district')
            state = request.POST.get('state')
            country = request.POST.get('country')
            exists = Address.objects.filter(user_id = user_id).exists()
            if not exists:
                address = Address(
                    user_id= user_id,
                    house_no = house_no,
                    recipient_name = recipient_name,
                    street_name = street_name,
                    village_name = village_name,
                    postal_code = postal_code,
                    district = district,
                    state = state,
                    country = country,
                    is_default = True                 

                 )
            else :
                address = Address(
                    user_id= user_id,
                    house_no = house_no,
                    recipient_name = recipient_name,
                    street_name = street_name,
                    village_name = village_name,
                    postal_code = postal_code,
                    district = district,
                    state = state,
                    country = country,      
                 )
            address.save()
            return redirect('user_profile')
    

    
def AddressView( request):
    if 'useremail' in request.session:
        email = request.session['useremail']
        user = CustomUser.objects.get(email = email)
        user_id = user.id
        address = Address.objects.filter(user_id = user_id) 
        context = {
            'user' : user,
            'address' : address
        }
    else :
        return redirect( 'user_login')
    return render(request, 'userprofile/address.html' , context)



def EditAddress( request, address_id):
    if request.method=='POST':   
        address=Address.objects.get(id=address_id)
        
        address.house_no = request.POST.get('house_no')
        address.recipient_name = request.POST.get('RecipientName')
        address.street_name = request.POST.get('street_name')
        address.village_name =  request.POST.get('Village')
        address.postal_code =  request.POST.get('postal_code')
        address.district =  request.POST.get('district')
        address.state =  request.POST.get('state')
        address.country =  request.POST.get('country')

        address.save()

        return redirect('user_profile')
    

    
def DeleteAddress(request,address_id):
    address=Address.objects.get(id=address_id)
    address.delete()
    return redirect('user_profile')



def DefaultAddress(request):
    if request.method =='POST':
        try:
            default_address_check = Address.objects.get(is_default=True)
            
            # If a default address exists, remove the old default address
            default_address_check.is_default = False
            default_address_check.save()
            
        except Address.DoesNotExist:
            # Handle the case where no default address exists
            pass

        address_id = request.POST.get("default_address")  # getting the address selected by the user
        
        try:
            # Attempt to retrieve the selected address
            address = Address.objects.get(id=address_id)
            address.is_default = True
            address.save()
        except Address.DoesNotExist:
            # Handle the case where the selected address doesn't exist
            raise Http404("The selected address does not exist")  # Raise Http404 to indicate a not found error

    return redirect('user_profile')


@login_required(login_url='/login/')
def MyOrders(request):
    if request.user:
        order_items = None
        user_email = request.session['useremail']
        print(user_email)
        user = CustomUser.objects.get(email=user_email)
        try:
            orders = Order.objects.filter(user=user)
            # Paginate the orders
            paginator = Paginator(orders, 10)  # Set the number of orders per page
            page = request.GET.get('page', 1)

            try:
                orders = paginator.page(page)
            except EmptyPage:
                orders = paginator.page(paginator.num_pages)

            order_items = OrderItem.objects.filter(order__in=orders).order_by('order').distinct('order')
        except:
            orders = None
            order_items = None

        context = {
            "orders": orders,
            "order_items": order_items
        }

        return render(request, "userprofile/my_orders.html", context)
    


@login_required(login_url='/login/')
def OrderDetails(request,order_id):
    
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    status=order.status
    context={
        "order_items":order_items,
        "order":order,
        "status":status
    }
    return render(request,"userprofile/order_details.html",context)





def OrderCancellation(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    orderItems = OrderItem.objects.filter(order = order)


    print("This all are my order items for a undestandngs-----------------",orderItems)
    print("This all are my order items for a undestandngs-----------------",orderItems)

    for i in orderItems:
        print(i)
        print("This is my Stock as per the varient--------",i.variant.stock)
        print("This is my Stock as per the varient--------",i.variant.stock)
        i.variant.stock +=  i.quantity
        varient = Variation.objects.get(id = i.variant.id)
        varient.stock +=  i.quantity
        varient.save()
        print("This is my stock after the cancel request ",i.variant.stock)
    print(order)
    
    # Update order status to 'Cancelled'
    order.status = 'Cancelled'
    order.save()

    # You may want to perform additional actions related to order cancellation here.

    order_items = OrderItem.objects.filter(order=order)
    status = order.status
    context = {
        "order_items": order_items,
        "order": order,
        "status": status
    }
    return render(request, "userprofile/order_details.html", context)




def OrderReturn(request,order_id):

    order=Order.objects.get(id=order_id)
    order.status='Return requested'
    order.save()

    order_items=OrderItem.objects.filter(order=order)
    status=order.status
    context={
        "order_items":order_items,
        "order":order,
        "status":status
    }
    return render(request,"userprofile/order_details.html",context)



# def change_password(request, user_id):
#     user = CustomUser.objects.get(id=user_id)
#     print("heyyyyy")
#     if request.method == "POST":
#         password = request.POST.get("password")
#         confirm_password = request.POST.get("c_password")
#         user_email =  request.session['useremail']

#         if password == confirm_password:
#             user.set_password(password)
#             print("=================================")
#             user.save()
            
#             print("=================================")
#             user = authenticate(request, email=user.email, password=password)
#             print("=================================")
#             if user:
#                 login(request, user)
#                 request.session['useremail'] = user_email
                
#             print("=================================")
#             print("hey its working")
#             messages.success(request, "Password changed successfully")
#             return redirect("user_profile")
#         else:
#             messages.error(request, "Passwords don't match")
#             return redirect("change_password", user_id=user_id)  # Provide the user_id parameter

#     return render(request, "userprofile\change_password")


def change_password(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    print("heyyyyy")
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        password = request.POST.get("password")
        confirm_password = request.POST.get("c_password")
        user_email = request.session['useremail']

        # Verify the current password before allowing a change
        if not user.check_password(current_password):
            messages.error(request, "Incorrect current password")
            return redirect("change_password", user_id=user_id)

        if password == confirm_password:
            user.set_password(password)
            print("=================================")
            user.save()


            # Re-authenticate the user with the new password
            user = authenticate(request, email=user.email, password=password)
            if user:
               login(request, user)
                
            print("=================================")
            print("hey its working")
            messages.success(request, "Password changed successfully")
            return redirect("change_password", user_id=user_id)
        else:
            messages.error(request, "Passwords don't match")
            return redirect("change_password", user_id=user_id)  # Provide the user_id parameter

    return render(request, "userprofile\change_password")


            
