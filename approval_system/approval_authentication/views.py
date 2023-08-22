from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.permissions import  IsAuthenticated

from .models import BlackListedToken, Approval, UserApproval, User
from .renderers import UserJSONRenderer
from .serializers import LoginSerializer, UserSerializer, ApprovalSerializer, UserApprovalSerializer
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegistrationSerializer


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't  have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            BlackListedToken.objects.create(token=refresh_token, user_id=request.user.id)

            return Response({"message": "User Logged Successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class ApprovalView(ModelViewSet):
    queryset = Approval.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ApprovalSerializer

    def create(self, request):
        serializer = ApprovalSerializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = Approval.objects.get(id=serializer.data['id'])
        instance.user_id = request.user.id
        instance.save()


        for user_id in serializer.data['users']:
            user = User.objects.get(id=user_id)
            user_approvals = UserApproval.objects.filter(approval=instance, user=user)
            if len(user_approvals) == 0:
                if instance.approval_id is None:
                    UserApproval.objects.create(approval=instance, user=user, active=True)
                else:
                    UserApproval.objects.create(approval=instance, user=user)
        return Response(serializer.data)


class UserApprovalView(ModelViewSet):
    queryset = UserApproval.objects.filter()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserApprovalSerializer

    def update(self, request, *args, **kwargs):
        serializer_data = request.data

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()



        user_approval = UserApproval.objects.get(id=request.data['id'])
        user_approval.approved = True
        user_approval.approval = Approval.objects.get(id=request.data['approval'])
        user_approval.save()
        approval = user_approval.approval

        approved_list = []

        for user in approval.users.all():
            if user == request.user:
                approved_list.append(UserApproval.objects.filter(user=user, approval=approval, approved=True, active=True))

        if approval.minimum_approver == len(approved_list):
            approval.approved = True
            approval.save()

            exists_approval = Approval.objects.filter(approval_id=approval.id).last()
            print(exists_approval)
            if exists_approval is not None:
                exists_approvals = UserApproval.objects.filter(approval=exists_approval)
                for exist_approval in exists_approvals:
                    exist_approval.active = True
                    exist_approval.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserApprovalAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserApprovalSerializer

    def list(self, request, *args, **kwargs):
        queryset = UserApproval.objects.filter(user=request.user, approved=False, active=True)
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
def index_view(request):
    return render(request, 'index.html')