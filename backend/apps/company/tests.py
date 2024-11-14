from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.users.models import CustomUser, UserRequest


class TestCompany(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        self.company = Company.objects.create(name="Test Company", owner=self.owner)
        self.company.members.add(self.owner)
        self.company.members.add(self.user)
        self.client.force_authenticate(user=self.owner)
        
    def test_appoint_admin(self):
        data = {'user': self.user.id}
        response = self.client.patch(f"/api/companies/companies/{self.company.id}/appoint_admin/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, self.company.admins.all())
        self.assertEqual(response.data['detail'], "User appointed as admin successfully.")
        
    def test_appoint_admin_user_not_member(self):
        new_user = CustomUser.objects.create_user(username='new_user', password='password')
        data = {'user': new_user.id}
        response = self.client.patch(f"/api/companies/companies/{self.company.id}/appoint_admin/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is not a member of the company")
        
    def test_appoint_admin_already_admin(self):
        self.company.admins.add(self.user)
        data = {'user': self.user.id}
        response = self.client.patch(f"/api/companies/companies/{self.company.id}/appoint_admin/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is already an admin of the company")
    
    def test_remove_admin(self):
        self.company.admins.add(self.user)
        data = {'user': self.user.id}
        response = self.client.patch(f"/api/companies/companies/{self.company.id}/remove_admin/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.user, self.company.admins.all())
        self.assertEqual(response.data['detail'], "User removed as admin successfully.")
    
    def test_remove_admin_user_not_admin(self):
        data = {'user': self.user.id}
        response = self.client.patch(f"/api/companies/companies/{self.company.id}/remove_admin/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is not an admin of the company")
        
        
class TestCompanyInvitation(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        self.company = Company.objects.create(name="Test Company", owner=self.owner)
        self.company.members.add(self.owner)

    def test_create_invitation(self):
        self.client.force_authenticate(user=self.owner)
        invitation_data = {"company": self.company.id, "receiver": self.user.id, "sender": self.owner.id}
        response = self.client.post("/api/companies/invitations/", data=invitation_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], CompanyInvitation.StatusChoices.PENDING)

    def test_list_invitations(self):
        invitation_1 = CompanyInvitation.objects.create(company=self.company, receiver=self.user, sender=self.owner)

        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/companies/invitations/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], CompanyInvitation.StatusChoices.PENDING)

    def test_create_invitation_with_not_owner(self):
        company_2 = Company.objects.create(name="Test Company 2", owner=self.owner)

        self.client.force_authenticate(user=self.user)
        invitation_data = {"company": company_2.id, "receiver": self.owner.id, "sender": self.user.id}

        response = self.client.post("/api/companies/invitations/", data=invitation_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_revoke_invitation(self):
        invitation = CompanyInvitation.objects.create(company=self.company, receiver=self.user, sender=self.owner)
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(f"/api/companies/invitations/{invitation.id}/revoke/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, CompanyInvitation.StatusChoices.REVOKED)
        self.assertEqual(response.data["status"], "R")


class TestCompanyRequest(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        self.company = Company.objects.create(name="Test Company", owner=self.owner)
        self.company.members.add(self.owner)

    def test_list_requests(self):
        user_request_1 = UserRequest.objects.create(
            company=self.company, sender=self.user, status=UserRequest.StatusChoices.PENDING
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/companies/requests/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], UserRequest.StatusChoices.PENDING)

    def test_approve_request(self):
        request = UserRequest.objects.create(company=self.company, sender=self.owner)
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(f"/api/companies/requests/{request.id}/approve/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertEqual(request.status, UserRequest.StatusChoices.APPROVED)
        self.assertEqual(response.data["status"], "A")

    def test_reject_request(self):
        request = UserRequest.objects.create(company=self.company, sender=self.owner)
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(f"/api/companies/requests/{request.id}/reject/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request.refresh_from_db()
        self.assertEqual(request.status, UserRequest.StatusChoices.REJECTED)
        self.assertEqual(response.data["status"], "R")
