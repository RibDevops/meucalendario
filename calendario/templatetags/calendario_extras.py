from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Retorna o valor de um dicionário pela chave"""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter
def divide(value, arg):
    """Divide o valor pelo argumento"""
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def multiply(value, arg):
    """Multiplica o valor pelo argumento"""
    try:
        return int(value) * int(arg)
    except ValueError:
        return 0
