from rest_framework import serializers
from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    paid_course_title = serializers.CharField(source='paid_course.title', read_only=True)
    paid_lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date', 'paid_course',
            'paid_course_title', 'paid_lesson', 'paid_lesson_title',
            'amount', 'payment_method'
        ]


class PaymentHistorySerializer(serializers.ModelSerializer):
    item_type = serializers.SerializerMethodField()
    item_title = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_date', 'item_type', 'item_title',
            'amount', 'payment_method'
        ]

    def get_item_type(self, obj):
        return 'Курс' if obj.paid_course else 'Урок'

    def get_item_title(self, obj):
        return obj.paid_course.title if obj.paid_course else obj.paid_lesson.title


class UserProfileSerializer(serializers.ModelSerializer):
    payment_history = PaymentHistorySerializer(
        many=True,
        read_only=True,
        source='payments'
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'city', 'avatar', 'date_joined',
            'payment_history'
        ]