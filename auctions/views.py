from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, AuctionListing, Category, Watchlist, Comment
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
    category = get_object_or_404(Category, id=category_id)
    listings = AuctionListing.objects.filter(category=category)

    return render(request, 'auctions/category_matches.html', {
        'category': category,
        'listings': listings
    })


def listing_details(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)

    # Watchlist logic
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
        form = forms.CreateCommentForm()
    else:
        in_watchlist = False
        form = None

    # Comments logic
    comments = Comment.objects.filter(listing=listing)

    return render(request, 'auctions/listing_details.html', {
        'listing': listing,
        'in_watchlist': in_watchlist,
        'comments': comments,
        'form': form
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

    return render(request, 'auctions/create.html', {
        'form': form
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

@login_required
def watchlist(request):
    listings = AuctionListing.objects.filter(watchlist__user=request.user)
    return render(request, 'auctions/watchlist.html', {
        'watchlist': listings
    })

"""
@login_required
def add_to_watchlist(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    watchlist_item = Watchlist.objects.create(request.user, listing)
    watchlist_item.save()
    return redirect('listing_details', listing.id)


@login_required
def remove_from_watchlist(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    user_watchlist = Watchlist.objects.delete(request.user, listing)
    user_watchlist.save()
    return redirect('listing_details', listing.id)
"""

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    watchlist_item = Watchlist.objects.filter(user=request.user, listing=listing).first()

    if watchlist_item:
        watchlist_item.delete()
    else:
        Watchlist.objects.create(user=request.user, listing=listing)
    
    return redirect('listing_details', listing_id)


"""
1. filter()

Tanto o first() quanto o exists() dependem de uma query feita com filter().

O método filter() do Django QuerySet retorna todos os objetos que correspondem às condições passadas como parâmetros. Por exemplo:

python

Watchlist.objects.filter(user=request.user, listing=listing)

Esta linha retornará todos os objetos da Watchlist em que:

    user é o request.user (o usuário atual),
    listing é o objeto AuctionListing que está sendo visualizado.

O resultado é um QuerySet (basicamente uma lista de objetos do banco de dados que corresponde à sua query).
2. first()

O método first() é usado em um QuerySet para retornar o primeiro item encontrado pela query, ou None se o QuerySet estiver vazio. É uma maneira rápida de pegar um único objeto quando você espera, ou deseja, apenas um item. Por exemplo:

python

watchlist_item = Watchlist.objects.filter(user=request.user, listing=listing).first()

Aqui, você está buscando o primeiro objeto da Watchlist que corresponde ao usuário e ao leilão específico. Se existir um item na watchlist do usuário para esse leilão, ele será retornado. Caso contrário, será retornado None.

Por que usar first()?

    Se você quer apenas um objeto, mas o filter() pode retornar múltiplos, first() garante que apenas o primeiro objeto seja retornado.
    No caso da watchlist, o relacionamento é de "um usuário com um item do leilão", então é esperado que haja no máximo um item correspondente na watchlist, e first() é usado para pegar esse único objeto (ou None, se não existir).

Alternativa: Você também poderia usar o método get() em vez de filter().first(), que retorna exatamente um objeto ou lança uma exceção se nenhum ou mais de um objeto for encontrado.

python

watchlist_item = Watchlist.objects.get(user=request.user, listing=listing)

No entanto, o get() levanta uma exceção se o objeto não existir, então você precisaria lidar com essa exceção (com try/except). O first() é mais simples nesse sentido, porque não lança erro se nenhum objeto for encontrado — ele só retorna None.
3. exists()

O método exists() retorna um valor booleano (True ou False), e é útil quando você só quer saber se algum objeto correspondente à query existe no banco de dados, sem precisar carregar os objetos completos.

python

in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()

Aqui, o exists() verifica se existe pelo menos um objeto na Watchlist que corresponda ao user e ao listing. Ele retorna:

    True, se a query encontrar pelo menos um objeto.
    False, se a query não encontrar nada.

Por que usar exists()?

    Ele é mais eficiente do que buscar os objetos completos, pois o banco de dados só precisa verificar se há registros que correspondem à query e não precisa carregar todos os dados dos objetos.
    É ideal quando você só quer saber se existe ou não um determinado item na watchlist.

Diferença entre first() e exists()

    first(): Retorna o primeiro objeto encontrado ou None (se não houver nenhum objeto).
    exists(): Retorna True ou False dependendo se existe ou não algum objeto correspondente à query.

Em resumo:

    Você usa first() quando precisa do objeto em si (ou None se não existir).
    Você usa exists() quando só precisa saber se o objeto existe (sem carregar os dados completos do objeto).
"""

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        form = forms.CreateCommentForm(request.POST)

        if form.is_valid():
            listing = get_object_or_404(AuctionListing, id=listing_id)
            comment = form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.save()
            return redirect('listing_details', listing_id)
    else:
        form = forms.CreateCommentForm()
    
    return render(request, 'auctions/listing_details.html', {
        'form': form
    })
    