from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Portfolio
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class PortfolioView(TemplateView):

    template_name: str = 'portfolio/portfolio.html'
    html_title: str = 'Portfolio'

    @method_decorator(login_required(login_url='login'))
    def get(self, request, *args, **kwargs) -> render:

        portfolio = Portfolio.objects.get(user=request.user)
        stocks_owned = portfolio.stocks_owned

        context = {
            'html_title': self.html_title,
            'portfolio': portfolio,
            'stocks_owned': stocks_owned
        }

        return render(request, self.template_name, context=context)