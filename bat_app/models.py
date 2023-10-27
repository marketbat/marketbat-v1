from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Assets(models.Model):
    BULLISH = 'Bullish'
    BEARISH = 'Bearish'
    NEUTRAL = 'Neutral'
    STRONG = 'Strong'
    NORMAL = 'Normal'
    WEAK = 'Weak'
    FOREX = 'Forex'
    CYRPTO = 'Crypto'
    ALL = 'All'
    FOREX = 'Forex'
    CRYPTOCURRENCY = 'Cryptocurrency'
    STOCKS = 'Stocks'
    BONDS = 'Bonds'
    COMMODITIES = 'Commodities'
    INDICES = 'Indices'
    ETFs = 'ETFs'
    REITs = 'REIT'
    NFTs = 'NFTs'
    OTHERS = 'Others'

    ASSET_CATEGORIES = (
        (ALL, 'All'),
        (FOREX, 'Forex'),
        (CRYPTOCURRENCY, 'Cryptocurrency'),
        (STOCKS, 'Stocks'),
        (COMMODITIES, 'Commodities'),
        (NFTs, 'Non-Fungible Tokens'),
        (INDICES, 'Indices'),
        (BONDS, 'Bonds'),
        (ETFs, 'Exchange-Traded Funds'),
        (REITs, 'Real Estate Investment Trusts'),
        (OTHERS, 'Others')
    )


    SENTIMENT_CHOICES = (
            (BULLISH, 'Bullish'),
            (BEARISH, 'Bearish'),
            (NEUTRAL, 'Neutral')
    )

    INTENSITY_CHOICES = (
            (STRONG, 'Strong'),
            (NORMAL, 'Normal'),
            (WEAK, 'Weak')
    )
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    market_price =  models.CharField(max_length=100, default="-")
    avatar = models.CharField(max_length=100, blank=True)
    trending = models.BooleanField(default=False)
    posts = models.ManyToManyField('Posts', related_name='asset_post', blank=True)
    category = models.CharField(max_length=100, choices=ASSET_CATEGORIES, default=OTHERS)
    subscribers = models.IntegerField(default=0)
    insights = models.TextField(blank=True)
    profiles_voted_bullish = models.ManyToManyField('Profile', related_name='bullish_assets', blank=True)
    profiles_voted_bearish = models.ManyToManyField('Profile', related_name='bearish_assets', blank=True)
    current_conversation_volume = models.IntegerField(default=0)
    yesterday_conversation_volume = models.IntegerField(default=0)
    current_conversation_intensity = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    current_sentiment = models.CharField(max_length=100, choices=SENTIMENT_CHOICES, default=NEUTRAL)
    week_conversation_volume = models.IntegerField(default=0)
    week_conversation_intensity = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    week_sentiment = models.CharField(max_length=100, choices=SENTIMENT_CHOICES, default=NEUTRAL)
    month_conversation_volume = models.IntegerField(default=0)
    month_sentiment = models.CharField(max_length=100, choices=SENTIMENT_CHOICES, default=NEUTRAL)
    month_conversation_intensity = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    alltime_conversation_volume = models.IntegerField(default=0)   
    alltime_conversation_intensity = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    alltime_sentiment = models.CharField(max_length=100, choices=SENTIMENT_CHOICES, default=NEUTRAL)
  


    def __str__(self):
        return f"{self.name}"
    
    def total_polls(self):
        return self.profiles_voted_bullish.count() + self.profiles_voted_bearish.count()

    def percent_bullish(self):
        total = self.total_polls()
        if total > 0:
            return (self.profiles_voted_bullish.count() / total) * 100
        else:
            return 0

    def percent_bearish(self):
        total = self.total_polls()
        if total > 0:
            return (self.profiles_voted_bearish.count() / total) * 100
        else:
            return 0
       

    def update_poll(self, profile, poll_type):
        # Check if the profile has already votedxwxw
        if poll_type == 'bullish':
            self.profiles_voted_bullish.add(profile)
        elif poll_type == 'bearish':
            self.profiles_voted_bearish.add(profile)

        self.save()
            

    def remove_poll(self, profile, poll_type):
        if poll_type == 'bullish':
            self.profiles_voted_bullish.remove(profile)
        elif poll_type == 'bearish':
            self.profiles_voted_bearish.remove(profile)
        
        self.save()
    
    def calculate_mean_sentiment(self):
        # Calculate the date 24 hours ago from now
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        # Calculate the date 7 days ago from now
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        # Calculate the date 30 days ago from now
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Calculate the mean polarity of articles made within the last 24 hours
        mean_article_polarity = self.articles.filter(
            article_date__gte=twenty_four_hours_ago
        ).aggregate(Avg('article_polarity'))['article_polarity__avg']

        # Calculate the mean polarity of posts made within the last 24 hours
        mean_post_polarity = self.posts.filter(
            post_date__gte=twenty_four_hours_ago
        ).aggregate(Avg('post_polarity'))['post_polarity__avg']

        # Calculate the mean polarity of articles made within the last 7 days
        mean_week_article_polarity = self.articles.filter(
            article_date__gte=seven_days_ago
        ).aggregate(Avg('article_polarity'))['article_polarity__avg']

        # Calculate the mean polarity of posts made within the last 7 days
        mean_week_post_polarity = self.posts.filter(
            post_date__gte=seven_days_ago
        ).aggregate(Avg('post_polarity'))['post_polarity__avg']

        # Calculate the mean polarity of articles made within the last 30 days
        mean_month_article_polarity = self.articles.filter(
            article_date__gte=thirty_days_ago
        ).aggregate(Avg('article_polarity'))['article_polarity__avg']

        # Calculate the mean polarity of posts made within the last 30 days
        mean_month_post_polarity = self.posts.filter(
            post_date__gte=thirty_days_ago
        ).aggregate(Avg('post_polarity'))['post_polarity__avg']

        # Calculate the overall mean polarity
        if mean_article_polarity is None and mean_post_polarity is None:
            mean_polarity = 0
        elif mean_article_polarity is None:
            mean_polarity = mean_post_polarity
        elif mean_post_polarity is None:
            mean_polarity = mean_article_polarity
        else:
            mean_polarity = (mean_article_polarity + mean_post_polarity) / 2

        # Update the current_sentiment based on the mean polarity
        if mean_polarity == 0.00:
            self.current_sentiment = 'Neutral'
        elif mean_polarity < 0.00:
            self.current_sentiment = 'Bearish'
        elif mean_polarity > 0.00:
            self.current_sentiment = 'Bullish'
        else:
            self.current_sentiment = 'Neutral'

        # Update the current_conversation_intensity
        self.current_conversation_intensity = mean_polarity

        # Update the current_conversation_volume
        current_conversation_volume = self.articles.filter(
            article_date__gte=twenty_four_hours_ago
        ).count() + self.posts.filter(
            post_date__gte=twenty_four_hours_ago
        ).count()
        self.current_conversation_volume = current_conversation_volume

        # Update the week_conversation_volume
        week_conversation_volume = self.articles.filter(
            article_date__gte=seven_days_ago
        ).count() + self.posts.filter(
            post_date__gte=seven_days_ago
        ).count()
        self.week_conversation_volume = week_conversation_volume

        # Update the month_conversation_volume
        month_conversation_volume = self.articles.filter(
            article_date__gte=thirty_days_ago
        ).count() + self.posts.filter(
            post_date__gte=thirty_days_ago
        ).count()
        self.month_conversation_volume = month_conversation_volume

        # Update the week_sentiment based on the mean polarity for the last 7 days
        if mean_week_article_polarity is None and mean_week_post_polarity is None:
            mean_week_polarity = 0
        elif mean_week_article_polarity is None:
            mean_week_polarity = mean_week_post_polarity
        elif mean_week_post_polarity is None:
            mean_week_polarity = mean_week_article_polarity
        else:
            mean_week_polarity = (mean_week_article_polarity + mean_week_post_polarity) / 2

        if mean_week_polarity == 0.00:
            self.week_sentiment = 'Neutral'
        elif mean_week_polarity < 0.00:
            self.week_sentiment = 'Bearish'
        elif mean_week_polarity > 0.00:
            self.week_sentiment = 'Bullish'
        else:
            self.week_sentiment = 'Neutral'

        self.week_conversation_intensity = mean_week_polarity

        # Update the month_sentiment based on the mean polarity for the last 30 days
        if mean_month_article_polarity is None and mean_month_post_polarity is None:
            mean_month_polarity = 0
        elif mean_month_article_polarity is None:
            mean_month_polarity = mean_month_post_polarity
        elif mean_month_post_polarity is None:
            mean_month_polarity = mean_month_article_polarity
        else:
            mean_month_polarity = (mean_month_article_polarity + mean_month_post_polarity) / 2

        if mean_month_polarity == 0.00:
            self.month_sentiment = 'Neutral'
        elif mean_month_polarity < 0.00:
            self.month_sentiment = 'Bearish'
        elif mean_month_polarity > 0.00:
            self.month_sentiment = 'Bullish'
        else:
            self.month_sentiment = 'Neutral'

        self.month_conversation_intensity = mean_month_polarity
        

        # Save the updated asset
        self.save()
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_dp_image', blank=True)
    cover_picture = models.ImageField(upload_to='profile_cover_image', blank=True)
    bio = models.TextField(blank=True)
    joined = models.DateTimeField( default=datetime.now)
    followers = models.ManyToManyField('Profile', related_name='profile_followers', blank=True)
    following = models.ManyToManyField('Profile', related_name='profile_following', blank=True)
    # Define choices for interests
    interests = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return f"{self.user.username}"




class Posts(models.Model):

    Bearish = 'Bearish'
    Bullish = 'Bullish'

    POST_SENTIMENT_CHOICES = (
            (Bullish, 'Bullish'),
            (Bearish, 'Bearish'),
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    asset = models.ManyToManyField(Assets, related_name='posts_asset', blank=True)
    post_text = models.TextField()
    post_image = models.ImageField(upload_to='post_images', blank=True)
    post_video = models.FileField(upload_to='post_videos', blank=True)
    likes = models.ManyToManyField('Profile', related_name='profile_likes', blank=True)
    comments = models.ManyToManyField('Comments', related_name='profile_comments', blank=True)
    reposts = models.ManyToManyField('Profile', related_name='profile_reposts', blank=True)
    post_date = models.DateTimeField(default=datetime.now)
    post_sentiment = models.CharField(max_length=100, choices=POST_SENTIMENT_CHOICES, null=True)
    post_polarity = models.DecimalField(default=0, decimal_places=2, max_digits=100)

    def __str__(self):
        return f"{self.post_text}"
    
class Articles(models.Model):
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE, related_name='articles')
    article_text = models.TextField()
    article_link = models.TextField()
    article_author =  models.CharField(max_length=100)
    article_date = models.DateTimeField(default=datetime.now)
    article_polarity = models.DecimalField(default=0, decimal_places=2, max_digits=100)
    

    def __str__(self):
        return f"{self.article_text}"
    
    def delete_old_articles(self):
        # Calculate the date 1 month ago from now
        one_month_ago = timezone.now() - timedelta(days=30)

        # Delete articles older than 1 month
        deleted_count, _ = Articles.objects.filter(
            asset=self.asset,
            article_date__lt=one_month_ago
        ).delete()

        return deleted_count


class Comments(models.Model):
    comment_text = models.TextField()
    comment_author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comment_author')
    comment_post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comment_post')
    comment_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.comment_text}"
    

    
class Notifications(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notification')
    text = models.TextField()
    read = models.BooleanField(default=False)
    time = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.text}"
    
class Conversation(models.Model):

    INBOX = "Inbox"
    REQUEST = "Request"

    MESSAGE_CATEGORY_CHOICES = (
        (INBOX, "Inbox"),
        (REQUEST, "Request")
    )

    participants = models.ManyToManyField(Profile, related_name="conversations")
    messages = models.ManyToManyField('Message', related_name="messages")
    category = models.CharField(max_length=100, choices=MESSAGE_CATEGORY_CHOICES, default=REQUEST)

    def __str__(self):
        return f"{self.participants}"
    
    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()
    

class Message(models.Model):
    TEXT = "Text"
    IMAGE = "Image"
    VIDEO = 'Video'

    CONTENT_TYPE_CHOICES = (
            (TEXT, 'Text'),
            (IMAGE, 'Image'),
            (VIDEO, 'Video'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default=TEXT)  # 'text', 'image', 'video'
    text = models.TextField()  # For captions
    media_file = models.FileField(upload_to='message_media', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Indicates if the message has been read

    def __str__(self):
        return f"{self.text}"
    

class Community(models.Model):
    admin = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    about = models.TextField()
    display_image = models.FileField(upload_to='community_dp', null=True, blank=True)
    cover_image = models.FileField(upload_to='community_cover', null=True, blank=True)
    participants = models.ManyToManyField(Profile, related_name="group_conversations")
    messages = models.ManyToManyField('CommunityMessage', related_name="group_messages", blank=True)
    date_started = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.name}"
    
    def get_last_message(self):
        return self.messages.order_by('-timestamp').first()
    

class CommunityMessage(models.Model):
    TEXT = "Text"
    IMAGE = "Image"
    VIDEO = 'Video'

    CONTENT_TYPE_CHOICES = (
            (TEXT, 'Text'),
            (IMAGE, 'Image'),
            (VIDEO, 'Video'),
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default=TEXT)  # 'text', 'image', 'video'
    text = models.TextField()  # For captions
    media_file = models.FileField(upload_to='message_media', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Indicates if the message has been read

    def __str__(self):
        return f"{self.text}"


class Signal(models.Model):
    BUY = 'Buy'
    SELL = 'Sell'
    BUY_STOP = 'Buy Stop'
    SELL_STOP = 'Sell Stop'
    BUY_LIMIT = 'Buy Limit'
    SELL_LIMIT = 'Sell Limit'
    
    ORDER_TYPE_CHOICES = (
        (BUY, 'Buy'),
        (SELL, 'Sell'),
        (BUY_STOP, 'Buy Stop'),
        (SELL_STOP, 'Sell Stop'),
        (BUY_LIMIT, 'Buy Limit'),
        (SELL_LIMIT, 'Sell Limit')
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_signal')
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE)
    chart = models.FileField(upload_to='signal_charts', null=True, blank=True)
    order_type = models.CharField(max_length=100, choices=ORDER_TYPE_CHOICES)
    analysis = models.TextField(blank=True)
    entry_price = models.CharField(max_length=100)
    takeprofit = models.CharField(max_length=100)
    stoploss = models.CharField(max_length=100)
    upvotes =  models.ManyToManyField('Profile', related_name='profile_upvotes', blank=True)
    downvotes =  models.ManyToManyField('Profile', related_name='profile_downvotes', blank=True)
    expiry = models.DateTimeField()

    def __str__(self):
        return f"{self.asset}"
    
class Explore(models.Model):
    image = models.FileField(upload_to='explore_images')
    news = models.TextField(blank=True)

class Data(models.Model):
    forex = models.FileField(upload_to='forex_data', blank=True)
    stocks = models.FileField(upload_to='stocks_data', blank=True)
    crypto = models.FileField(upload_to='crypto_data', blank=True)
    nft = models.FileField(upload_to='nft_data', blank=True)
    commodities = models.FileField(upload_to='commodities_data', blank=True)
    indices = models.FileField(upload_to='indices_data', blank=True)
    bonds = models.FileField(upload_to='bonds_data', blank=True)
    etfs = models.FileField(upload_to='etfs_data', blank=True)
    reits = models.FileField(upload_to='reits_data', blank=True)
    others = models.FileField(upload_to='others_data', blank=True)


class DailyPollStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    total_polls = models.PositiveIntegerField(default=0)
    bullish_count = models.PositiveIntegerField(default=0)
    bearish_count = models.PositiveIntegerField(default=0)
    bullish_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    bearish_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

# Create a signal to update daily statistics when a new poll is added
#@receiver(post_save, sender=Poll)  # Adjust this based on your Poll model
#def update_daily_statistics(sender, instance, **kwargs):
    # Logic to update DailyPollStatistics based on the poll
   #pass  # You need to calculate and update daily statistics here

# Create a management command to reset profile fields and save daily statistics
from django.core.management.base import BaseCommand
from datetime import date

class ResetDailyPollStatisticsCommand(BaseCommand):
    help = 'Reset daily poll statistics and save daily counts.'

    def handle(self, *args, **options):
        # Get all user profiles
        profiles = Profile.objects.all()  # Adjust based on your profile model

        # Iterate through profiles and reset fields
        for profile in profiles:
            profile.bullish_field = 0
            profile.bearish_field = 0
            profile.save()

            # Calculate and save the daily statistics
            daily_stat = DailyPollStatistics(
                user=profile.user,
                date=date.today(),
                total_polls=profile.total_polls(),  # You need to implement this method in your model
                bullish_count=profile.profiles_voted_bullish.count(),
                bearish_count=profile.profiles_voted_bearish.count(),
                bullish_percentage=profile.percent_bullish(),
                bearish_percentage=profile.percent_bearish(),
            )
            daily_stat.save()
