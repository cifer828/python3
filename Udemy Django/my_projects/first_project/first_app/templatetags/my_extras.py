from django import template

register = template.Library()


@register.filter(name='rua')
def rua(value_arg1, arg2):
    """
    This cuts out all value of arg from the string
    """
    value, arg1 = value_arg1
    return value.replace(arg1, "").replace(arg2, '')


# register.filter('rua', rua)


@register.filter(name='chain_filter')
def chain_filter(value, arg1):
    """
    enable multiple arguments in filter
    """
    return value, arg1

#
# register.filter('chain_filter', chain_filter)


