from django.shortcuts import render
from django.views.generic import TemplateView
from core.models import Stock
from portfolio.models import Portfolio
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class DashboardView(TemplateView):

    template_name: str = 'dashboard/dashboard.html'
    html_title: str = 'Dashboard'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, *args, **kwargs) -> render:

        all_stocks = Stock.objects.all()
        portfolio = Portfolio.objects.get(user=request.user)

        context = {
            'html_title': self.html_title,
            'stocks': all_stocks,
            'portfolio': portfolio,
        }

        return render(request, self.template_name, context=context)


