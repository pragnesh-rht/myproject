from rest_framework import serializers
from .models import Post, Images, Bidder
from users.models import User, Profile

from django.utils import timezone


class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = (
            'id', 'url', 'author', 'title', 'description', 'content', 'initial_price', 'current_price', 'date_posted',
            'date_end',)
        read_only_fields = ('current_price',)


class ImagesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Images
        fields = ('id', 'url', 'post', 'post_image',)


class BidderSerializer(serializers.HyperlinkedModelSerializer):
    bid_author = serializers.ReadOnlyField(source='bid_author.username')

    class Meta:
        model = Bidder
        fields = ('id', 'url', 'post', 'prices', 'bid_author',)

    def validate(self, data):
        if data['post'].author == self.context['request'].user:
            raise serializers.ValidationError('You cannot bid on your own post')

        if data['post'].date_end >= timezone.now():
            if data['post'].initial_price <= data['prices'] > data['post'].current_price:
                return data
            else:
                raise serializers.ValidationError('values must be higher than the current bid and minimum price')
        raise serializers.ValidationError('Sorry, the bidding time is over :(')


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'url', 'user', 'image',)
