from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, AuctionListing, Category
from . import forms


def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    return render(request, 'auctions/categories.html', {
        'categories': Category.objects.all()
    })


def category_matches(request, category_id):
    category = Category.objects.get(id=category_id)
    listings = AuctionListing.objects.filter(category=category)

    return render(request, 'auctions/category_matches.html', {
        'category': category,
        'listings': listings
    })


def listing_details(request, listing_id):
    return render(request, 'auctions/listing_details.html', {
        'listing': AuctionListing.objects.get(id=listing_id)
    })

"""
@login_required
def create(request):
    if request.method == "POST":
        form = forms.CreateListingForm(request.POST, request.FILES)

        if form.is_valid():
            listing = AuctionListing.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                starting_bid=form.cleaned_data['starting_bid'],
                photo=form.cleaned_data['photo']
            )
            return redirect('listing_details', listing.id)
    else:
        form = forms.CreateListingForm()

    return render(request, "auctions/create.html", {
        "form": form
    })
"""

@login_required
def create(request):
    if request.method == "POST":
        form = forms.CreateListingForm(request.POST, request.FILES)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.listed_by = request.user
            listing.save()
            return redirect('listing_details', listing.id)
    else:
        form = forms.CreateListingForm()

    return render(request, "auctions/create.html", {
        "form": form
    })

"""
1. listing = form.save(commit=False)

Essa linha salva os dados do formulário no modelo, mas ainda não os insere no banco de dados. O parâmetro commit=False diz ao Django para criar uma instância do modelo (AuctionListing), 
preencher os campos com os dados do formulário, mas não salvar no banco imediatamente.

Isso é útil quando você precisa adicionar ou modificar campos que não foram incluídos no formulário, como neste caso, onde o campo listed_by precisa ser preenchido com o usuário logado.

Em termos práticos, o que acontece é:

    O Django pega os dados validados do formulário (name, description, starting_bid, photo, category) e os coloca em uma nova instância de AuctionListing.
    O objeto listing está pronto, mas ainda não existe no banco de dados.

2. listing.listed_by = request.user

Aqui, você está manualmente associando o campo listed_by ao usuário que está logado no momento. Como esse campo não foi incluído no formulário
(porque queremos que seja automaticamente associado), você precisa fazer isso programaticamente.

Esta linha simplesmente atribui o valor de request.user (que é o usuário atual) ao campo listed_by do objeto listing.

Agora, o objeto listing está completo com todos os campos preenchidos (incluindo os que não foram submetidos pelo formulário).

3. listing.save()

Finalmente, essa linha salva de fato o objeto listing no banco de dados. Antes disso, o objeto existia apenas na memória (como uma instância de Python), 
mas após essa linha, ele será persistido no banco de dados com todos os campos preenchidos, incluindo o listed_by.
"""