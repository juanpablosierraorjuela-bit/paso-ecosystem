from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class AdminRequiredMixin(UserPassesTestMixin):
    '''Solo permite acceso si el usuario es ADMIN'''
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'

    def handle_no_permission(self):
        return redirect('home')  # O a una página de error 403

class EmployeeRequiredMixin(UserPassesTestMixin):
    '''Solo permite acceso si el usuario es EMPLEADO'''
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'EMPLOYEE'
