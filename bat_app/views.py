from django.shortcuts import render
from .models import Assets, Profile, Posts, Articles, Message, Conversation, Signal, Community, CommunityMessage, Notifications, Comments, Explore, Data
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from .sentiment import *
import requests
from django.db.models import Max
from django.db import IntegrityError
from django.db.models import Count
import csv
import io

def create_assets_from_csv():
    try:
        data = Data.objects.first()
        if data:
            base_url = "http://marketbat.pythonanywhere.com/"  # Replace with your actual base URL
            csv_relative_url = data.forex.url

            # Concatenate the base URL and relative URL to get the absolute URL
            csv_url = f"{base_url}{csv_relative_url}"

            # Download the CSV file from the URL
            response = requests.get(csv_url)
            
            if response.status_code == 200:
                csv_data = response.content.decode('utf-8-sig')
                
                # Create a temporary in-memory file to read the CSV data
                with io.StringIO(csv_data) as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        try:
                            # Remove the BOM from the column name
                            code = row.get('\ufeff"CODE"', row.get('CODE'))
                            base_currency = row["BASE_CURRENCY"]
                            quote_currency = row["QUOTE_CURRENCY"]
                            name = f"{base_currency}_{quote_currency}"
                            

                            # Check if the asset with the same name already exists
                            if not Assets.objects.filter(name=name).exists():
                                Assets.objects.create(name=name, symbol=code, category="Forex")
                                print("Added", name)
                        except Exception as e:
                            print("Error processing row:", e)
            else:
                print("Failed to download CSV file. Status Code:", response.status_code)
        else:
            print("No data found in the database.")
    except Exception as ex:
        print("Error:", ex)

def create_assets_from_csv_stocks():
    try:
        data = Data.objects.first()
        if data:
            base_url = "http://marketbat.pythonanywhere.com/"  # Replace with your actual base URL
            csv_relative_url = data.stocks.url

            # Concatenate the base URL and relative URL to get the absolute URL
            csv_url = f"{base_url}{csv_relative_url}"

            # Download the CSV file from the URL
            response = requests.get(csv_url)
            
            if response.status_code == 200:
                csv_data = response.content.decode('utf-8-sig')
                
                # Create a temporary in-memory file to read the CSV data
                with io.StringIO(csv_data) as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        try:
                            symbol = row.get('Symbol')
                            name = row.get('Name')
                            price = row.get('Last Sale')
                            

                            # Check if the asset with the same name already exists
                            if not Assets.objects.filter(name=name).exists():
                                Assets.objects.create(name=name, symbol=symbol, category="Stocks", market_price=price)
                                print("Added", name)
                        except Exception as e:
                            print("Error processing row:", e)
            else:
                print("Failed to download CSV file. Status Code:", response.status_code)
        else:
            print("No data found in the database.")
    except Exception as ex:
        print("Error:", ex)

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '404.html', status=500)


@csrf_exempt
def index(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    community = Posts.objects.all().order_by('-id')
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    profile = Profile.objects.get(user=request.user)
   
    context = {
        'assets': assets,
        'trending': trending,
        'community': community,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,
        'profile': profile
    }
    return render(request, 'pro_index.html', context)

@csrf_exempt
def messages(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    conversations = Conversation.objects.filter(participants=profile)
    conversations = conversations.annotate(last_message_time=Max('message__timestamp'))
    conversations = conversations.order_by('-last_message_time')
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    assets = Assets.objects.all()
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]

    context = {
        'conversations': conversations,
        'profile': profile,
        'trending': trending,
        'assets': assets,
        'top_polls': top_polls,
       
    }
    return render(request, 'message.html', context)


@csrf_exempt
def conversation(request, conversation_id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversations = Conversation.objects.filter(participants=profile)
    messages = Message.objects.filter(conversation=conversation)
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    assets = Assets.objects.all()
    unread_messages = Message.objects.filter(conversation=conversation)

    for message in unread_messages:
        if profile != message.sender:
            message.read = True
            message.save()


    context = {
        'conversation': conversation,
        'conversations': conversations,
        'profile': profile,
        'messages': messages,
        'trending': trending,
        'assets': assets,
    }


    return render(request, 'message_detail.html', context)

@csrf_exempt
def send_message(request, conversation_id):
     if request.method == 'POST':
        try:
            text = request.POST.get('text')
            if request.user.is_authenticated:
                profile = Profile.objects.get(user=request.user)
            else:
                profile = None
            content_type = "Text"
            print(text)

            # Check if an image is provided
            if 'image' in request.FILES:
                image = request.FILES['image']
                content_type = "Image"
            else:
                image = None  # Set it to None if not provided
            conversation = get_object_or_404(Conversation, id=conversation_id)
            message = Message.objects.create(conversation=conversation, sender=profile, content_type=content_type, text=text, media_file=image)
            conversation.messages.add(message)
            conversation.save()

            return JsonResponse({'status': 'success', 'message': text})
        except:
            return JsonResponse({'status': 'error', 'message': text})


@csrf_exempt
def asset_details(request, id):
    asset = get_object_or_404(Assets, pk=id)
    assets = Assets.objects.all()
    posts = Posts.objects.filter(asset=asset).order_by('-id')
    articles = Articles.objects.filter(asset=asset).order_by('-id')
    context = {
        'assets': assets,
        'asset': asset,
        'posts': posts,
        'articles': articles,
        }
    return render(request, 'assets.html', context)


@csrf_exempt
def explore(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    posts = Posts.objects.all().order_by('-id')
    conversations = Conversation.objects.filter(participants=profile)
    explore_top = Explore.objects.first()
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    context = {
        'assets': assets,
        'trending': trending,
        'profile': profile,
        'posts': posts,
        'conversations': conversations,
        'explore_top': explore_top,
        'top_polls': top_polls,
        'category_choices': category_choices
        }
    return render(request, 'explore.html', context)


@csrf_exempt
def update_poll(request, asset_id, poll_type):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        asset = Assets.objects.get(id=asset_id)
        if poll_type == 'bullish':
            asset.update_poll(profile, 'bullish')
            asset.remove_poll(profile, 'bearish')
        elif poll_type == 'bearish':
            asset.update_poll(profile, 'bearish')
            asset.remove_poll(profile, 'bullish')
        

        total_polls = asset.total_polls()
        percent_bullish = asset.percent_bullish()
        percent_bearish = asset.percent_bearish()

        return JsonResponse({
            'message': 'success',
            'total_polls': total_polls,
            'percent_bullish': percent_bullish,
            'percent_bearish': percent_bearish
        })

    return JsonResponse({'message': 'not_authenticated'})


@csrf_exempt
def search_polls_assets(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    search_term = request.GET.get('search_term', '')
    assets = Assets.objects.filter(name__icontains=search_term)[:50]
    
    asset_data = []
    for asset in assets:
        percent_bullish = asset.percent_bullish()
        percent_bearish = asset.percent_bearish()
        
        # Check if the user's profile has voted for this asset as bullish
        is_bullish = profile in asset.profiles_voted_bullish.all()
        
        # Check if the user's profile has voted for this asset as bearish
        is_bearish = profile in asset.profiles_voted_bearish.all()

        asset_data.append({
            'id': asset.id,
            'name': asset.name,
            'percent_bullish': percent_bullish,
            'percent_bearish': percent_bearish,
            'total_polls': asset.total_polls(),
            'isBullish': is_bullish,
            'isBearish': is_bearish
        })

    return JsonResponse({'assets': asset_data})

@csrf_exempt
def polls(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    conversations = Conversation.objects.filter(participants=profile)
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]

    context = {
        'assets': assets,
        'trending': trending,
        'profile': profile,
        'conversations': conversations,
        'top_polls': top_polls
    }
    return render(request, 'polls.html', context)


@csrf_exempt
def signals(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    assets = Assets.objects.all()
    conversations = Conversation.objects.filter(participants=profile)
    order_types =  [choice[0] for choice in Signal.ORDER_TYPE_CHOICES] 
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    signals = Signal.objects.exclude(profile=profile)
    my_signals = Signal.objects.filter(profile=profile)
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]

    context = {
        'assets': assets,
        'trending': trending,
        'profile': profile,
        'conversations': conversations,
        'signals': signals,
        'order_types': order_types,
        'my_signals': my_signals,
        'top_polls': top_polls,
        }
    return render(request, 'signals.html', context)

@csrf_exempt
def create_signal(request):
     if request.method == 'POST':
        # Retrieve data from the request
        signal_chart = request.FILES.get('signalChart')
        signal_asset = request.POST.get('signalAsset')
        signal_order_type = request.POST.get('signalOrderType')
        signal_entry_price = request.POST.get('signalEntryPrice')
        signal_take_profit = request.POST.get('signalTakeProfit')
        signal_stop_loss = request.POST.get('signalStopLoss')
        signal_analysis = request.POST.get('signalAnalysis')
        signal_expiry = request.POST.get('signalExpiry')
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
        else:
            profile = None

        try:
            asset = Assets.objects.get(id=signal_asset)
            Signal.objects.create(
                profile=profile, 
                asset=asset,
                chart = signal_chart,
                order_type = signal_order_type,
                analysis = signal_analysis,
                entry_price = str(signal_entry_price),
                takeprofit = str(signal_take_profit),
                stoploss = str(signal_stop_loss),
                expiry = signal_expiry
            )
            return JsonResponse({'message': 'success'})
        except IntegrityError as e:
            print("Database Error:", str(e))  # Print the database error for debugging
            return JsonResponse({'status': 'error', 'message': 'There was an issue posting signal, please check all values again.'}, status=400)
        except Exception as e:
            print("Error:", str(e))  # Print the general exception for debugging
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred while posting the signal.'}, status=400)
@csrf_exempt
def get_signal_details(request, signal_id):
    signal = get_object_or_404(Signal, pk=signal_id)
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    # You can customize this to return additional fields like analysis
    profileInUpvotes = profile in signal.upvotes.all()
    profileInDownvotes = profile in signal.downvotes.all()
    profileOwner = signal.profile == profile

    profile
    signal_data = {
        'chartUrl': signal.chart.url,
        'name': signal.asset.name,
        'id': signal.id,
        'profileName': signal.profile.user.username,
        'profilePicture': signal.profile.profile_picture.url,
        'orderType': signal.order_type,
        'entryPrice': signal.entry_price,
        'takeProfit': signal.takeprofit,
        'stopLoss': signal.stoploss,
        'upvotes': signal.upvotes.count(),
        'downvotes': signal.downvotes.count(),
        'expiry': signal.expiry,
        'analysis': signal.analysis, # Add the analysis field here
        'profileInUpvotes': profileInUpvotes,
        'profileInDownvotes': profileInDownvotes,
        'profileOwner': profileOwner


    }
    return JsonResponse(signal_data)


@csrf_exempt
def update_vote(request, signal_id, vote_type):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        signal = Signal.objects.get(id=signal_id)
        if vote_type == 'upvote':
            signal.upvotes.add(profile)
            signal.downvotes.remove(profile)
            
        elif vote_type == 'downvote':
            signal.downvotes.add(profile)
            signal.upvotes.remove(profile)
            
        signal.save()

        upvotes_count = signal.upvotes.count()
        downvotes_count = signal.downvotes.count()

        return JsonResponse({
            'message': 'success',
            'upvotes_count': upvotes_count,
            'downvotes_count': downvotes_count
        })

    return JsonResponse({'message': 'not_authenticated'})

@csrf_exempt
def community(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    conversations = Conversation.objects.filter(participants=profile)
    context = {
        'assets': assets,
        'trending': trending,
        'profile': profile,
        'conversations': conversations,
        }
    return render(request, 'home.html', context)

@csrf_exempt
def home(request):
    create_assets_from_csv()
    #create_assets_from_csv_stocks()
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
        
    assets = Assets.objects.all()
    
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    posts = Posts.objects.all().order_by('-id')
    conversations = Conversation.objects.filter(participants=profile)
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]
    context = {
        'assets': assets,
        'trending': trending,
        'posts': posts,
        'profile': profile,
        'conversations': conversations,
        'top_polls': top_polls,
        }
    return render(request, 'feeds.html', context)



@csrf_exempt
def communities(request):
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    conversations = Conversation.objects.filter(participants=profile)
    other_communities = Community.objects.exclude(participants=profile)
    my_communities = Community.objects.filter(participants=profile)
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]
    context = {
        'assets': assets,
        'profile': profile,
        'trending': trending,
        'conversations': conversations,
        'other_communities':  other_communities,
        'my_communities': my_communities,
        'top_polls': top_polls,
        }
    return render(request, 'communities.html', context)


@csrf_exempt
def create_community(request):
     if request.method == 'POST':
        # Retrieve data from the request
        community_name = request.POST.get('communityName')
        community_about = request.POST.get('communityAbout')
        community_dp = request.FILES.get('communityDP')
        community_cover_photo = request.FILES.get('communityCoverPhoto')
        
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
        else:
            profile = None

        try:
           community = Community.objects.create(
                admin=profile, 
                name = community_name,
                about = community_about,
                display_image = community_dp,
                cover_image = community_cover_photo,
            )
           
           community.participants.add(profile)
           community.save()
           text = f"You successfully created '{community.name}' community."
           notifications = Notifications.objects.create(profile=community.admin, text=text)
           notifications.save()
           return JsonResponse({'message': 'success'})
        except IntegrityError as e:
            print("Database Error:", str(e))  # Print the database error for debugging
            return JsonResponse({'status': 'error', 'message': 'There was an issue posting signal, please check all values again.'}, status=400)
        except Exception as e:
            print("Error:", str(e))  # Print the general exception for debugging
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred while posting the signal.'}, status=400)


@csrf_exempt
def view_community(request, community_id):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    community = get_object_or_404(Community, id=community_id)
    messages = CommunityMessage.objects.filter(community=community)
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    assets = Assets.objects.all()
    unread_messages = CommunityMessage.objects.filter(community=community)

    for message in unread_messages:
        if profile != message.sender:
            message.read = True
            message.save()


    context = {
        'community': community,
        'profile': profile,
        'messages': messages,
        'trending': trending,
        'assets': assets,
    }

    return render(request, 'community_detail.html', context)

@csrf_exempt
def send_community_message(request, community_id):
     if request.method == 'POST':
        try:
            text = request.POST.get('text')
            if request.user.is_authenticated:
                profile = Profile.objects.get(user=request.user)
            else:
                profile = None
            content_type = "Text"
            print(text)

            # Check if an image is provided
            if 'image' in request.FILES:
                image = request.FILES['image']
                content_type = "Image"
            else:
                image = None  # Set it to None if not provided
            community = get_object_or_404(Community, id=community_id)
            message = CommunityMessage.objects.create(community=community, sender=profile, content_type=content_type, text=text, media_file=image)
            community.messages.add(message)
            community.save()

            return JsonResponse({'status': 'success', 'message': text})
        except:
            return JsonResponse({'status': 'error', 'message': text})
        
@csrf_exempt
def leave_community(request, community_id):
     if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                    profile = Profile.objects.get(user=request.user)
            else:
                    profile = None
            community = get_object_or_404(Community, id=community_id)
            community.participants.remove(profile)
            community.save()
            text = f"{profile.display_name} left your '{community.name}' community."
            notifications = Notifications.objects.create(profile=community.admin, text=text)
            notifications.save()
            return JsonResponse({'status': 'success', 'message': 'You have succesfully left the community.'})
        except:
            return JsonResponse({'status': 'error', 'message': 'Unexpected error, please try again.'})

@csrf_exempt
def join_community(request, community_id):
     if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                    profile = Profile.objects.get(user=request.user)
            else:
                    profile = None
            community = get_object_or_404(Community, id=community_id)
            community.participants.add(profile)
            community.save()
  
            text = f"{profile.display_name} joined your '{community.name}' community."
            notifications = Notifications.objects.create(profile=community.admin, text=text)
            notifications.save()
            
            return JsonResponse({'status': 'success', 'message': 'You have succesfully joined the community.'})
        except:
            return JsonResponse({'status': 'error', 'message': 'Unexpected error, please try again.'})
        


@csrf_exempt
def delete_community(request, community_id):
     if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                    profile = Profile.objects.get(user=request.user)
            else:
                    profile = None
            community = get_object_or_404(Community, id=community_id)
            community.delete()
            text = f"You deleted your '{community.name}' community."
            notifications = Notifications.objects.create(profile=community.admin, text=text)
            notifications.save()

            return JsonResponse({'status': 'success', 'message': 'You have succesfully deleted the community.'})
        except:
            return JsonResponse({'status': 'error', 'message': 'Unexpected error, please try again.'})
        

@csrf_exempt
def notifications(request):
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    conversations = Conversation.objects.filter(participants=profile)
    notifications = Notifications.objects.filter(profile=profile).order_by('-id')
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]

    for notification in notifications:
            notification.read = True
            notification.save()

    context = {
        'assets': assets,
        'profile': profile,
        'trending': trending,
        'conversations': conversations,
        'notifications': notifications,
        'top_polls': top_polls,
        }
    return render(request, 'notifications.html', context)

@csrf_exempt
def profile(request):
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    conversations = Conversation.objects.filter(participants=profile)
    posts = Posts.objects.filter(profile=profile).order_by('-id')
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]
    context = {
        'assets': assets,
        'profile': profile,
        'trending': trending,
        'conversations': conversations,
        'posts': posts,
        'top_polls': top_polls,
        }
    return render(request, 'profile.html', context)

@csrf_exempt
def user_profile(request, username):
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    user_profile = Profile.objects.get(username=username)
    assets_with_total_polls = [(asset, asset.total_polls()) for asset in assets]
    sorted_assets = sorted(assets_with_total_polls, key=lambda x: x[1], reverse=True)
    top_polls = [asset[0] for asset in sorted_assets[:50]]
    
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    
    if profile == user_profile:
        
        return redirect('profile')
    
    else:
        conversations = Conversation.objects.filter(participants=profile)
        posts = Posts.objects.filter(profile=user_profile).order_by('-id')
        context = {
            'assets': assets,
            'profile': profile,
            'trending': trending,
            'conversations': conversations,
            'posts': posts,
            'user_profile': user_profile,
            'top_polls': top_polls,
            }
        return render(request, 'view_profile.html', context)


   
@csrf_exempt
def comment(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        post = Posts.objects.get(id=post_id)
        profile = Profile.objects.get(user=request.user)
        author = post.profile
        comment = Comments.objects.create(comment_text=text, comment_author=profile, comment_post=post)
        post.comments.add(comment)
        post.save()
        try:
            text = f"{profile.display_name} commented on your post."
            notifications = Notifications.objects.create(profile=author, text=text)
            notifications.save()
        except:
            pass
        return JsonResponse({'status': 'success', 'message': post.comments.count()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



@csrf_exempt
def like_post(request, post_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        profile = Profile.objects.get(user=request.user)
        post = Posts.objects.get(id=post_id)
        author = post.profile
        likes = post.likes.all()
        if action:
            if profile not in likes:
                post.likes.add(profile)
        
                post.save()
                try:
                    if post.profile:
                        text = f"{profile.display_name} reacted to your post ❤️."
                        notifications = Notifications.objects.create(profile=author, text=text)
                        notifications.save()

                except:
                    pass
                message = f'You are now liking post {post_id}'
            else:
                post.likes.remove(profile)
    
                post.save()
                message = f'You have unliked post {post_id}'
        return JsonResponse({'status': 'success', 'message': post.likes.count()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    

@csrf_exempt
def follow_profile(request, profile_id):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        user_profile = Profile.objects.get(id=profile_id)
        followers = user_profile.followers.all()

        if profile not in followers:
            user_profile.followers.add(profile)
            profile.following.add(user_profile)
            user_profile.save()
            profile.save()
            try:
                text = f"{profile.display_name} started following you🥳."
                notifications = Notifications.objects.create(profile=user_profile, text=text)
                notifications.save()
            except:
                pass
            message = f'Following'
        else:
            user_profile.followers.remove(profile)
            profile.following.remove(user_profile)
            message = f'Follow'
            user_profile.save()
            profile.save()
        print('done')
        return JsonResponse({'status': 'success', 'message': message, 'count': user_profile.followers.count()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def save_profile(request):
    if request.method == 'POST':
        user_profile = Profile.objects.get(user=request.user)
        updated_bio = request.POST.get('bio')
        interests = request.POST.get('interests')

        # Update the profile data
        user_profile.bio = updated_bio
        user_profile.interests = interests

        # Handle image uploads if necessary
        if 'avatar' in request.FILES:
            user_profile.profile_picture = request.FILES['avatar']
        if 'cover' in request.FILES:
            user_profile.cover_picture = request.FILES['cover']

        user_profile.save()

        return JsonResponse({'message': 'Profile changes saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def calendar(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    conversations = Conversation.objects.filter(participants=profile)
    context = {
        'assets': assets,
        'trending': trending,
        'conversations': conversations,
        }
    return render(request, 'calendar.html', context)

@csrf_exempt
def news(request):
    assets = Assets.objects.all()
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    conversations = Conversation.objects.filter(participants=profile)
    context = {
        'assets': assets,
        'trending': trending,
        'conversations': conversations,
        }
    return render(request, 'news.html', context)

@csrf_exempt
def blog(request):
    assets = Assets.objects.all()
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
    else:
        profile = None
    context = {
        'assets': assets,
        'trending': trending,
        }
    return render(request, 'blog.html', context)
@csrf_exempt
def forex_assets(request):
    assets = Assets.objects.filter(category = "Forex")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'forex.html', context)

@csrf_exempt
def crypto_assets(request):
    assets = Assets.objects.filter(category = "Cryptocurrency")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'crypto.html', context)

@csrf_exempt
def stocks_assets(request):
    assets = Assets.objects.filter(category = "Stocks")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'stocks.html', context)

@csrf_exempt
def nft_assets(request):
    assets = Assets.objects.filter(category = "NFTs")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'nft.html', context)

@csrf_exempt
def commodities_assets(request):
    assets = Assets.objects.filter(category = "Commodities")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'commodities.html', context)

@csrf_exempt
def indices_assets(request):
    assets = Assets.objects.filter(category = "Indices")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'indices.html', context)

@csrf_exempt
def bonds_assets(request):
    assets = Assets.objects.filter(category = "Bonds")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'bonds.html', context)


@csrf_exempt
def etfs_assets(request):
    assets = Assets.objects.filter(category = "ETFs")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'etfs.html', context)

@csrf_exempt
def reits_assets(request):
    assets = Assets.objects.filter(category = "REITs")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'reits.html', context)

@csrf_exempt
def other_assets(request):
    assets = Assets.objects.filter(category = "Others")
    trending = Assets.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    category_choices = [choice[0] for choice in Assets.ASSET_CATEGORIES] 
    sentiment_choices = [choice[0] for choice in Assets.SENTIMENT_CHOICES]
    
    context = {
        'assets': assets,
        'trending': trending,
        'category_choices': category_choices,
        'sentiment_choices': sentiment_choices,

        }
    return render(request, 'others.html', context)

@csrf_exempt
def company(request):
    assets = Assets.objects.all()
    context = {
        'assets': assets,
        }
    return render(request, 'company.html', context)


@csrf_exempt
def learn(request):
    assets = Assets.objects.all()
    context = {
        'assets': assets,
        }
    return render(request, 'learn.html', context)

@csrf_exempt
def smartbat(request):
    assets = Assets.objects.all()
    context = {
        'assets': assets,
        }
    return render(request, 'smartbat.html', context)

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        display_name = firstname + " " + lastname
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User already exists. '}, status=400)
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            profile = Profile.objects.create(user=user, username=username, display_name = display_name )
            auth.login(request, user)
            return JsonResponse({'message': 'success'})
    return render(request, 'index.html')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        # print(password)
        if "@" in email:
            user = auth.authenticate(email=email, password=password)
        else:
            user = auth.authenticate(username=email, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            return JsonResponse({'message': 'success'})
        else:
            return JsonResponse({'error': 'Invalid login credentials, please check your email adress and password.'}, status=400)
    return render(request, 'index.html')

@csrf_exempt
def logout(request):
    auth.logout(request)
    return redirect('home')

@csrf_exempt
def post(request, id):
    if request.method == 'POST':
        text = request.POST.get('text')
        sentiment = request.POST.get('sentiment')
        asset = get_object_or_404(Assets, pk=id)
        profile = Profile.objects.get(user=request.user)
        print(asset)
        print(text)
        print(sentiment.capitalize())
        Posts.objects.create(profile=profile, asset = asset, post_text=text, post_sentiment=sentiment.capitalize())
    return JsonResponse({'message': 'success'})

def extract_assets_from_post(post_text):
    matched_assets = []
    post_text = post_text.lower()
    assets = Assets.objects.all()


    # Define custom stop words for common English words and conjunctions
    custom_stop_words = set()
    custom_stop_words.update(["is", "at", "and", "or", "the", "of", "in", "to", "for"])

    for asset in assets:
        asset_name = asset.name.lower()
        asset_symbol = asset.symbol.lower()

        # Split the asset name into individual words
        asset_name_words = asset_name.split()

        # Filter out stop words and short words (e.g., "a", "an")
        asset_name_words = [word for word in asset_name_words if word not in custom_stop_words and len(word) > 1]

        # Check if any word in the asset name is in the post_text
        if any(word in post_text for word in asset_name_words) or asset_symbol in post_text:
            matched_assets.append(asset)

    return matched_assets


@csrf_exempt
def postfeed(request):
    if request.method == 'POST':
        text = request.POST.get('text')

        if 'image' in request.FILES:
            image = request.FILES['image']
        else:
            image = None  

        if 'video' in request.FILES:
            video = request.FILES['video']
        else:
            video = None  
       
        profile = Profile.objects.get(user=request.user)
        post = Posts.objects.create(profile=profile, post_text=text, post_image=image, post_video=video)
        results = extract_assets_from_post(text)
        print(results)
        for asset in results:
            post.asset.add(asset)
            asset.posts.add(post)
            
        post.save()
        asset.save()
    return JsonResponse({'message': 'success'})


def clear_last():
    first_50_assets = Articles.objects.all()[:1]
    # now 730
    first_50_asset_ids = first_50_assets.values_list('id', flat=True)
    Articles.objects.exclude(id__in=first_50_asset_ids).delete()

def update_data():
    assets = Assets.objects.all()
    for asset in assets:
        asset.calculate_mean_sentiment()
        asset.save()

    articles = Articles.objects.all()
    for article in articles:
        deleted_count = article.delete_old_articles()
        print(f"Deleted {deleted_count} old articles.")
