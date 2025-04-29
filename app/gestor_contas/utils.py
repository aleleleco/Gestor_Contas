from .models import Submenu

def geraSubMenu(pagina):
    submenu = Submenu.objects.filter(pagina=pagina)


    return submenu
