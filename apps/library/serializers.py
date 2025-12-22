from rest_framework import serializers

from .models import (
    BookCategory,
    Book,
    LibraryMember,
    LibraryCard,
    BookIssue,
    BookReturn,
    LibraryFine,
    BookReservation,
)


class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class LibraryMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryMember
        fields = '__all__'


class LibraryCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCard
        fields = '__all__'


class BookIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookIssue
        fields = '__all__'


class BookReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReturn
        fields = '__all__'


class LibraryFineSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryFine
        fields = '__all__'


class BookReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReservation
        fields = '__all__'
