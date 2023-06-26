from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from academy.models import Course, CourseModule, CourseModuleSubscription, CourseSubscription, Quiz, ShortVideo, ShortVideoSubscription

from nutrify_app.models import Commercial, Company, CompanyIndividualMembership, Individual
from nutrify_commercial.models import CommercialSubscription
from nutrify_commercial.utils import check_commercial_subscription
from users.models import User
from nutrify.middleware import CustomLogging
from academy.utils import has_purchased_all_modules, has_purchased_course


class IsAdmin(BasePermission):
    """
    Allows access only to Admin.
    """

    def has_permission(self, request, view):
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID)
        user = get_object_or_404(User, id=account_id)
        return user.role == User.SUPER_USER
    
class IsAdminOrNutrifyUser(BasePermission):
    """
    Allows access only to Admin.
    """

    def has_permission(self, request, view):
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID)
        user = get_object_or_404(User, id=account_id)
        return user.role == User.SUPER_USER or user.role == User.NUTRIFY_USER


class IsIndividual(BasePermission):
    """
    Allows access only to Individuals.
    """

    def has_permission(self, request, view):
        try:
            if view.action == 'reset_password_on_request':
                return True
        except:
            CustomLogging.process_exception(None, request, None)
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID)
        return account_id == str(request.user.id) and Individual.objects.filter(user__id=account_id).exists()


class IsCompany(BasePermission):
    """
    Allows access only to Company.
    """

    def has_permission(self, request, view):
        return CompanyIndividualMembership.objects.filter(individual__user=request.user,
                                                          company__id=request.META.get(
                                                              settings.HEADER_ACCOUNT_ID),
                                                          status=CompanyIndividualMembership.OPEN,
                                                          is_admin=True).exists()


class IsCommercialCompany(BasePermission):
    """
    Allow access only to commercial company
    """

    def has_permission(self, request, view):
        return Commercial.objects.filter(company__id=request.META.get(settings.HEADER_ACCOUNT_ID, None)).exists()


class HasCommercialSubscription(BasePermission):
    """
    Allows access only to commercial who have purchased subscriptions
    """

    def has_permission(self, request, view):
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID, None)
        if account_id is not None:
            commercial = Commercial.objects.filter(
                company__id=account_id).first()
            if commercial:
                commercial_subscribed = CommercialSubscription.objects.filter(
                    commercial=commercial).first()
                if commercial_subscribed:
                    if check_commercial_subscription(commercial_subscribed):
                        return True
        return False


class IsCompanyApprovedByNutrifyAdmin(BasePermission):
    """
    Allow access to only those companies approved by the nutrify admin.
    """

    def has_permission(self, request, view):
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID)
        try:
            company_individual_membership = CompanyIndividualMembership.objects.get(
                individual__user=request.user,
                company__id=account_id,
                status=CompanyIndividualMembership.OPEN,
                is_admin=True)
            return company_individual_membership.company.is_approved_by_nutrify_admin == Company.ACCEPTED
        except CompanyIndividualMembership.DoesNotExist:
            return False


class HasCommercialRole(BasePermission):
    """
    Allow access to only commercial users.
    """

    def has_permission(self, request, view):
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID)
        try:
            company_individual_membership = CompanyIndividualMembership.objects.get(
                individual__user=request.user,
                company__id=account_id,
                status=CompanyIndividualMembership.OPEN,
                is_admin=True)
            return company_individual_membership.company.role == Company.COMMERCIAL

        except CompanyIndividualMembership.DoesNotExist:
            return False


class IsModulePurchased(BasePermission):
    """
    Allow access to modules which have been purchased using 
    module id
    """

    def has_permission(self, request, view):
        account_id = request.META.get(settings.HEADER_ACCOUNT_ID, None)
        if account_id is not None:
            individual = Individual.objects.filter(user__id=account_id).first()
        module = CourseModule.objects.filter(id=view.kwargs['pk']).first()
        if individual and module:
            # check if specific module is purchased
            if CourseModuleSubscription.objects.filter(individual=individual, module_purchased=module).exists():
                return True
            # check if course is purchased
            course_purchased = CourseSubscription.objects.filter(
                individual=individual, course_purchased=module.course).first()
            if course_purchased:
                return True
        return False


class IsCourseOrAllModulePurchased(BasePermission):
    """
    Allow access to modules or courses which have been purchased
    using quiz-id
    """

    def has_permission(self, request, view):
        course_id = None
        quiz = Quiz.objects.filter(id=view.kwargs['pk']).first()
        if quiz:
            course_id = quiz.course.id
        course_module = CourseModule.objects.filter(
            id=view.kwargs['pk']).first()
        if course_module:
            course_id = course_module.course.id
        individual = Individual.objects.filter(
            user__id=request.user.id).first()
        course_purchased = has_purchased_course(individual, course_id)
        all_modules_purchased = has_purchased_all_modules(
            individual, course_id)

        return course_purchased or all_modules_purchased


class IsShortVideoPurchased(BasePermission):
    def has_permission(self, request, view):
        individual = Individual.objects.get(user=request.user)
        video = ShortVideo.objects.filter(id=view.kwargs['pk']).first()
        is_purchased = ShortVideoSubscription.objects.filter(
            short_video_purchased=video, individual=individual).exists()
        return is_purchased
