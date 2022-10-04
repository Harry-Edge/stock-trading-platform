from django import template

register = template.Library()


@register.simple_tag
def get_return_investment_for_user_if_applicable(stock, user):
    return stock.return_investment_for_user_if_applicable(user)
