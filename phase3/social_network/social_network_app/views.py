from django.shortcuts import render, redirect
from django.views.generic import View
from social_network_app import forms
from django.urls import reverse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.db.models import Q
from isbnlib import meta
from datetime import datetime, timedelta
from django.contrib import messages


class IndexView(View):
    def get(self, request):
        items = {}
        if request.user.id:
            items = Item.objects.filter(owner=request.user)
        print(items)
        return render(request, 'index.html', {'items': items})


class RegisterView(View):
    user_form = forms.UserForm()

    def get(self, request):
        return render(request, 'register.html', {'user_form': self.user_form})

    def post(self, request):
        self.user_form = forms.UserForm(data=request.POST)
        # if user input is valid then new user will be created
        if self.user_form.is_valid():
            user = self.user_form.save(commit=False)
            user.set_password(self.user_form.cleaned_data['password'])
            user.username = self.user_form.cleaned_data['email'].lower()
            # user.is_active = False
            user.save()

            return HttpResponseRedirect(reverse('social_network_app:login'))
        else:
            # user input is not valid
            print(self.user_form.errors)
            return render(request, 'register.html', {'user_form': self.user_form})


class LoginView(View):
    login_form = forms.LoginForm()

    def get(self, request):
        return render(request, 'login.html', {'login_form': self.login_form})

    def post(self, request):
        self.login_form = forms.LoginForm(data=request.POST)
        if self.login_form.is_valid():
            user = authenticate(username=self.login_form.cleaned_data['email'], password=self.login_form.cleaned_data['password'])
            if user and user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return HttpResponse("invalid login details")
        else:
            print('Login failed')
            return HttpResponse("invalid login details")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class UserItemsView(View):
    def get(self, request, user_id):
        location_available_items = {}
        location_unavailable_items = {}
        borrow_requests = {}
        if user_id:
            if request.user.id != user_id:
                # location null if it is borrowed
                try:
                    br = Borrow.objects.filter(is_returned=0).values_list('item', flat=True)
                except:
                    br = []
                friend_state = 0
                try:
                    friend_state = Friend.objects.get((Q(sender_user=user_id ) & Q(receiver_user=request.user)) | (Q(receiver_user=user_id ) & Q(sender_user=request.user))).state
                except:
                    pass
                if friend_state == 0:
                    location_available_items = Item.objects.filter(Q(owner=user_id) & Q(view=3) & ~Q(id__in=br))
                    location_unavailable_items = Item.objects.filter(Q(owner=user_id) & Q(view=3) & Q(id__in=br))
                else:
                    location_available_items = Item.objects.filter(Q(owner=user_id) & Q(view__gte=friend_state) & ~Q(id__in=br))
                    location_unavailable_items = Item.objects.filter(Q(owner=user_id) & Q(view__gte=friend_state) & Q(id__in=br))
            else:  # own items

                location_available_items = Item.objects.filter(Q(owner=request.user))


        return render(request, 'user_items_list.html', {'location_unavailable_items': location_unavailable_items, 'location_available_items': location_available_items,
                                                        'borrow_requests': borrow_requests })

    def post(self, request, user_id):
        print(request.POST)

        if user_id == request.user.id:
            if request.POST['submit_type'] == 'save':
                item = Item()
                item.owner_id = int(user_id)
                item.type = request.POST['type']
                item.title = request.POST['title']
                item.artist = request.POST['artist']
                item.genre = request.POST['genre']
                item.year = request.POST['year']
                item.location = request.POST['location']
                item.view = request.POST['view']
                item.detail = request.POST['detail']
                item.borrow = request.POST['borrow']
                item.comment = request.POST['comment']
                item.search = request.POST['search']
                if request.POST['isbn'] != '':
                    metadata = None
                    try:
                        metadata = meta(isbn=int(request.POST['isbn']))
                    except:
                        messages.warning(request, 'ISBN Number is wrong! Item couldn\'t be added' )
                        return redirect('/user_items_list/' + str(user_id))
                    if metadata is None:
                        messages.warning(request, 'Meta data couldn\'t be obtained' )
                        return redirect('/user_items_list/' + str(user_id))
                    else:
                        item.title = metadata['Title']
                        item.year = metadata['Year']
                        item.artist = metadata['Authors'][0]

                if item.detail > item.view:
                    item.view = item.detail
                    messages.warning(request, 'Detail permission cannot have higher priority than view permission. View permission also be set ' + STATE_TYPE[int(item.detail)])

                if item.borrow > item.view:
                    item.borrow = item.view
                    messages.warning(request, 'Borrow permission cannot have higher priority than view permission. Borrow permission also be set ' + STATE_TYPE[int(item.view)])

                if item.detail > item.comment:
                    item.comment = item.detail
                    messages.warning(request, 'Detail permission cannot have higher priority than comment permission. Comment permission also be set ' + STATE_TYPE[int(item.detail)])
                item.save()
                messages.success(request, 'Item is added successfully.')
                return redirect('/user_items_list/' + str(user_id))
            if request.POST['submit_type'] == 'returned':
                borrow_item = Borrow.objects.get(item_id=request.POST['item_id'], is_returned=0)
                borrow_item.is_returned = 1
                borrow_item.save()
                messages.success(request, 'Item is returned.')
                return redirect('/user_items_list/' + str(user_id))
            else:  # lend
                item_id = request.POST['item_id']

                if request.POST['returned_date'] == '':
                    taking_date = datetime.now()
                    return_date = taking_date + timedelta(weeks=2)
                    Borrow(user_id=request.POST['requested_user'], item_id=item_id, taken_date=datetime.now(), returned_date=return_date).save()
                else:
                    Borrow(user_id=request.POST['requested_user'], item_id=item_id, taken_date=datetime.now(), returned_date=request.POST['returned_date']).save()
                borrow_request = BorrowRequest.objects.get(user_id=request.POST['requested_user'], item_id=item_id)
                borrow_request.delete()
                messages.warning(request, 'Item lent')
                return redirect(('/user_items_list/' + str(user_id)))


class FriendsView(View):
    def get(self, request):
        friends = {}
        if request.user:
            friends = Friend.objects.filter(Q(sender_user=request.user) & ~Q(state=0))
            friends = friends | Friend.objects.filter(Q(receiver_user=request.user) & ~Q(state=0))

        friend_requests = {}
        if request.user:
            friend_requests = Friend.objects.filter(Q(receiver_user=request.user) & Q(state=0))

        return render(request, 'friendships.html', {'friends': friends, 'friend_requests':friend_requests })

    def post(self, request):
        selected_value = int(request.POST['selectpicker'])
        friend_req_id = int(request.POST['friend_id'])
        friend_request = Friend.objects.get(id=friend_req_id)
        friend_request.state = selected_value
        friend_request.save()
        return redirect('/friendships/')


class BorrowRequestsView(View):
    def get(self, request):
        borrow_requests = {}
        if request.user:
            borrow_requests = BorrowRequest.objects.filter(Q(user=request.user) & ~Q(item__owner=request.user) ).order_by('request_date')
        # TODO borrowedlanınca requestlerden sill!!!!!
        borrowed_items = Borrow.objects.filter(user=request.user, is_returned=0)

        returned_items = Borrow.objects.filter(user=request.user, is_returned=1)

        return render(request, 'borrow_requests.html', {'borrow_requests': borrow_requests, 'borrowed_items': borrowed_items, 'returned_items': returned_items })

    def post(self, request):
        # rate
        rate = request.POST['rate']
        borrow_id = request.POST['borrow_id']
        borrow = Borrow.objects.get(id=borrow_id)
        borrow.rate = rate
        borrow.save()
        return redirect('/borrow_requests/')


class AllItemsView(View):
    def get(self, request):
        # viewable
        try:
            state = Friend.objects.get(Q(receiver_user=request.user) | Q(sender_user=request.user))
            #TODO hatalıııı state -> itemın ownerı ile request.user statei çekilmeli
            s_users = Friend.objects.filter(receiver_user=request.user).values_list('sender_user', flat=True)
            r_users = Friend.objects.filter(sender_user=request.user).values_list('receiver_user', flat=True)
        except:
            state = 0
            s_users = []
            r_users = []

        viewable_items = Item.objects.filter(~Q(view=0) & ~Q(owner=request.user)&
                                               (Q(view=3) |
                                                (Q(owner_id__in=s_users) & Q(view__gte=state))
                                                 | Q(owner_id__in=r_users) & Q(view__gte=state)))
        # borrowable
        already_requested = BorrowRequest.objects.filter(user=request.user).values_list('item', flat=True)
        borrowable_items = Item.objects.filter(~Q(id__in=already_requested) & ~Q(owner=request.user) & ~Q(borrow=0) &
                                               (Q(borrow=3) |
                                                (Q(owner_id__in=s_users) & Q(borrow__gte=state))
                                                 | Q(owner_id__in=r_users) & Q(borrow__gte=state)))

        viewable_items = viewable_items.exclude(pk__in=borrowable_items)
        return render(request, 'all_items.html', {'borrowable_items': borrowable_items, 'viewable_items': viewable_items})

    def post(self, request):

        item = Item.objects.get(id=int(request.POST['item_id']))
        b_request = BorrowRequest(user=request.user, item=item, request_date=datetime.now())
        b_request.save()
        return redirect('/all_items/')


class ItemView(View):
    def get(self, request, item_id):
        if item_id:
            item = Item.objects.get(id=item_id)
            try:
                state = Friend.objects.get(Q(sender_user=request.user) & Q(receiver_user=item.owner) |
                                           Q(receiver_user=request.user) & Q(sender_user=item.owner)).state
            except:
                state = 0
            print(state)
            viewable = False
            detailable = False
            if (item.view >= state and state != 0) or item.view == 3:
                viewable = True
            if (item.detail >=state and state != 0) or item.detail == 3:
                detailable = True

            comments = Comment.objects.filter(item=item_id)

        return render(request, 'item.html', {'item': item, 'comments': comments})

    def post(self, request, item_id):
        print(request.POST)
        if request.POST['submit_type'] == "save_comment":
            comment_text = request.POST['comment_text']
            item = Item.objects.get(id=item_id)
            Comment(user=request.user, item=item, text=comment_text, date=datetime.now()).save()
            return redirect('/item/' + str(item_id))
        else:
            BorrowRequest(user=request.user, item_id=item_id, request_date=datetime.now()).save()
            return redirect('/item/' + str(item_id))


class AllUsersView(View):
    def get(self, request):
        users = User.objects.filter(~Q(id=request.user.id))
        return render(request, 'all_users.html',{'users': users} )

